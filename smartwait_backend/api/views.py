from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Restaurant, Table, Prediction, Queue
from .serializers import (
    RestaurantSerializer,
    TableSerializer,
    PredictionSerializer,
    QueueSerializer
)
import random
from .utils import calculate_wait_time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# ---------------- VIEWSETS ---------------- #

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer


class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer


# ---------------- HELPER FUNCTIONS ---------------- #

def update_queue_positions(restaurant):
    waiting = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at")

    for index, q in enumerate(waiting, start=1):
        if q.position != index:
            q.position = index
            q.save(update_fields=["position"])


def auto_seat_customers(restaurant):
    waiting_queue = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at")

    first = waiting_queue.first()

    if first:
        first.status = "seated"
        first.position = None
        first.save()

        # ✅ FREE a table (IMPORTANT FIX)
        restaurant.occupied_tables = max(
            0,
            restaurant.occupied_tables - 1
        )
        restaurant.save()


# ---------------- API FUNCTIONS ---------------- #

from django.shortcuts import get_object_or_404

@api_view(['POST'])
def join_queue(request):
    restaurant_id = request.data.get("restaurant")
    name = request.data.get("name")
    party_size = request.data.get("party_size")

    # ✅ validation
    if not restaurant_id or not name or not party_size:
        return Response({"error": "Missing fields"}, status=400)

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # ✅ current queue length
    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    # ✅ assign position
    position = queue_length + 1

    # ✅ create entry
    Queue.objects.create(
        restaurant=restaurant,
        name=name,
        party_size=party_size,
        position=position,
        status="waiting"
    )

    # ✅ update positions
    update_queue_positions(restaurant)

    # ✅ calculate wait
    wait_time = calculate_wait_time(restaurant)

    # ✅ log ML data
    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time,
        queue_length=queue_length + 1,
        occupied_tables=restaurant.occupied_tables,
        total_tables=restaurant.total_tables
    )

    # 🔥 SEND WEBSOCKET UPDATE (INSIDE FUNCTION)
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
    "queue_updates",
    {
        "type": "send_update",
        "data": {
            "restaurant_id": restaurant.id,
            "event": "joined_queue",
            "wait_time": round(wait_time),
            "queue_length": queue_length + 1
        }
    }
)

    # ✅ RETURN RESPONSE (LAST LINE)
    return Response({
        "status": "waiting",
        "position": position,
        "estimated_wait": round(wait_time)
    })


@api_view(['POST'])
def leave_queue(request):
    restaurant_id = request.data.get("restaurant")

    entry = Queue.objects.filter(
        restaurant_id=restaurant_id,
        status="waiting"
    ).order_by("joined_at").first()

    if entry:
        restaurant = entry.restaurant

        entry.status = "left"
        entry.save()

        update_queue_positions(restaurant)

        wait_time = calculate_wait_time(restaurant)

        Prediction.objects.create(
            restaurant=restaurant,
            wait_time=wait_time,
            queue_length=Queue.objects.filter(
                restaurant=restaurant,
                status="waiting"
            ).count(),
            occupied_tables=restaurant.occupied_tables,
            total_tables=restaurant.total_tables
        )
    # 🔥 SEND WEBSOCKET UPDATE
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "queue_updates",
        {
            "type": "send_update",
            "data": {
                "restaurant_id": restaurant.id,
                "event": "left_queue"
        }
    }
)

    return Response({"status": "left"})


@api_view(['GET'])
def predict_wait(request, restaurant_id):
    from django.shortcuts import get_object_or_404
    from api.train_model import train

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Step 1: simulate real flow
    auto_seat_customers(restaurant)

    # Step 2: update queue positions
    update_queue_positions(restaurant)

    # Step 3: calculate wait
    wait_time = calculate_wait_time(restaurant)

    # Step 4: small variation
    wait_time += random.randint(-2, 2)
    wait_time = max(1, round(wait_time))

    # 🔥 capture features
    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    # 🔥 store data
    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time,
        queue_length=queue_length,
        occupied_tables=restaurant.occupied_tables,
        total_tables=restaurant.total_tables
    )

    # 🔁 Auto retrain every 20 data points
    if Prediction.objects.count() % 20 == 0:
        print("🔁 Retraining model...")
        train()

    # 🔥 get position
    first_waiting = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at").first()

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "queue_updates",
        {
            "type": "send_update",
            "data": {
                "restaurant_id": restaurant.id,
                "wait_time": wait_time,
                "position": first_waiting.position if first_waiting else 0
        }
    }
)

    return Response({
        "wait_time": wait_time,
        "confidence": random.randint(80, 95),
        "position": first_waiting.position if first_waiting else 0
    })

@api_view(['GET'])
def recommend_restaurants(request):
    restaurants = Restaurant.objects.all()

    results = []

    for r in restaurants:
        wait = calculate_wait_time(r)

        # 🔥 simple hybrid score
        score = (
            -wait                      # shorter wait = better
            - r.occupied_tables * 2    # less crowded = better
        )

        results.append({
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "score": score,
            "wait_time": round(wait)
        })

    # sort best first
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return Response(results)