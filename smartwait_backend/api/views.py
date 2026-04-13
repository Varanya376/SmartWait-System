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

@api_view(['POST'])
def join_queue(request):
    restaurant_id = request.data.get("restaurant")
    name = request.data.get("name")
    party_size = request.data.get("party_size")

    restaurant = Restaurant.objects.get(id=restaurant_id)

    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    # ✅ Assign correct position
    position = queue_length + 1

    entry = Queue.objects.create(
        restaurant=restaurant,
        name=name,
        party_size=party_size,
        position=position,
        status="waiting"
    )

    update_queue_positions(restaurant)

    wait_time = calculate_wait_time(restaurant)

    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time
    )

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
            wait_time=wait_time
        )

    return Response({"status": "left"})


@api_view(['GET'])
def predict_wait(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    # ✅ Step 1: simulate seating
    auto_seat_customers(restaurant)

    # ✅ Step 2: update queue
    update_queue_positions(restaurant)

    # ✅ Step 3: calculate wait
    wait_time = calculate_wait_time(restaurant)

    # ✅ Step 4: small variation
    wait_time += random.randint(-2, 2)
    wait_time = max(1, round(wait_time))

    # STORE prediction
    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time
    )

    # ✅ Get current front of queue
    first_waiting = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at").first()

    return Response({
        "wait_time": wait_time,
        "confidence": random.randint(80, 95),
        "position": first_waiting.position if first_waiting else 0
    })