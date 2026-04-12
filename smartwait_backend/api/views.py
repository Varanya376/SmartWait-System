from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Restaurant, Table, Prediction, Queue
from .serializers import RestaurantSerializer, TableSerializer, PredictionSerializer, QueueSerializer


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

@api_view(['POST'])
def join_queue(request):
    restaurant_id = request.data.get("restaurant")
    name = request.data.get("name")
    party_size = request.data.get("party_size")

    # 🔥 STEP 1: create entry FIRST
    new_entry = Queue.objects.create(
        restaurant_id=restaurant_id,
        name=name,
        party_size=party_size
    )

    # 🔥 STEP 2: get all waiting queues
    queues = Queue.objects.filter(
        restaurant_id=restaurant_id,
        status="waiting"
    ).order_by("joined_at")

    # 🔥 STEP 3: assign positions properly
    for index, q in enumerate(queues):
        q.position = index + 1
        q.save()

    # 🔥 STEP 4: return correct position
    return Response({
        "message": "Joined queue",
        "position": new_entry.position,
        "estimated_wait": new_entry.position * 5
    })

@api_view(['POST'])
def leave_queue(request):
    restaurant_id = request.data.get("restaurant")
    name = request.data.get("name")

    try:
        queue = Queue.objects.filter(
            restaurant_id=restaurant_id,
            name=name,
            status="waiting"
        ).earliest("joined_at")

        queue.status = "left"
        queue.save()

        return Response({"message": "Left queue"})

    except Queue.DoesNotExist:
        return Response({"message": "Not found"}, status=404)