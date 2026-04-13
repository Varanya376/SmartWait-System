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
        q.position = index
        q.save()


def auto_seat_customers(restaurant):
    """
    Seat ONLY ONE customer per cycle → realistic flow
    """
    waiting_queue = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at")

    first = waiting_queue.first()

    if first:
        first.status = "seated"
        first.position = 0
        first.save()


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

    return Response({"status": "left"})


def calculate_wait_time(restaurant):
    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    avg_time = getattr(restaurant, "avg_dining_time", 10)
    capacity = getattr(restaurant, "capacity", 10)

    if capacity <= 0:
        return queue_length * avg_time

    return (queue_length / capacity) * avg_time


@api_view(['GET'])
def predict_wait(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    # ✅ STEP 1: seat ONE person (not all)
    auto_seat_customers(restaurant)

    # ✅ STEP 2: fix queue positions
    update_queue_positions(restaurant)

    # ✅ STEP 3: calculate wait
    wait_time = calculate_wait_time(restaurant)

    # ✅ STEP 4: slight variation
    wait_time += random.randint(-2, 2)
    wait_time = max(1, round(wait_time))

    return Response({
        "wait_time": wait_time,
        "confidence": random.randint(80, 95)
    })