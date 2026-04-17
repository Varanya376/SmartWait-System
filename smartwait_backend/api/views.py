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
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes


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

class StaffDashboardView(APIView):
    permission_classes = [IsAuthenticated]

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  

# ---------------- HELPER FUNCTIONS ---------------- #

def sync_restaurant_tables(restaurant):
    occupied = Table.objects.filter(
        restaurant=restaurant,
        status__in=["OCCUPIED", "RESERVED"]
    ).count()

    total = Table.objects.filter(restaurant=restaurant).count()

    restaurant.occupied_tables = occupied
    restaurant.total_tables = total
    restaurant.save()


def update_queue_positions(restaurant):
    waiting = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at")

    for index, q in enumerate(waiting, start=1):
        if q.position != index:
            q.position = index
            q.save(update_fields=["position"])


def send_realtime_update(restaurant, event, wait_time):
    channel_layer = get_channel_layer()

    update_queue_positions(restaurant)

    queue = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at")

    tables = Table.objects.filter(restaurant=restaurant)

    async_to_sync(channel_layer.group_send)(
        "queue_updates",
        {
            "type": "send_update",
            "message": event,
            "wait_time": wait_time,
            "restaurant_id": restaurant.id,
            "queue": QueueSerializer(queue, many=True).data,
            "tables": TableSerializer(tables, many=True).data
        }
    )

def get_safe_wait_time(restaurant):
    queue_count = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    wait_time = calculate_wait_time(restaurant)

    if queue_count > 0:
        return max(5, round(wait_time))
    return max(0, round(wait_time))

def process_queue(restaurant):
    queue = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).order_by("joined_at")

    free_tables = Table.objects.filter(
        restaurant=restaurant,
        status="FREE"
    )

    for q, table in zip(queue, free_tables):
        q.status = "seated"
        q.position = None
        q.save()

        table.status = "OCCUPIED"
        table.save()

    # update restaurant table counts
    sync_restaurant_tables(restaurant)

    # update remaining queue positions
    update_queue_positions(restaurant)

# ---------------- API FUNCTIONS ---------------- #

User = get_user_model()

@api_view(['POST'])
def register(request):
    data = request.data

    if User.objects.filter(email=data["email"]).exists():
        return Response(
            {"error": "User already exists"},
            status=400
        )

    user = User.objects.create(
        username=data["email"],
        email=data["email"],
        password=make_password(data["password"]),
        role=data.get("role", "customer")
    )

    return Response({"message": "User created"})

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, username=email, password=password)

    if user is not None:
        login(request, user)

        return Response({
            "message": "Logged in",
            "role": user.role,
            "restaurant_id": user.restaurant.id if user.restaurant else None
        })

    return Response({"error": "Invalid credentials"}, status=400)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out"})

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get("email")

    user = User.objects.filter(email=email).first()

    if user:
        user.set_password("newpassword123")  # simulate reset
        user.save()

    return Response({"message": "Password reset (simulated)"})

@api_view(['POST'])
def simulate_rush(request):
    restaurant_id = request.data.get("restaurant")

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    for i in range(5):
        Queue.objects.create(
            restaurant=restaurant,
            name=f"Rush {i}",
            party_size=random.randint(1, 5),
            status="waiting"
)

    update_queue_positions(restaurant)

    wait_time = get_safe_wait_time(restaurant)

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"message": "Rush simulated"})

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def join_queue(request):
    restaurant_id = request.data.get("restaurant")
    name = request.data.get("name")
    party_size = request.data.get("party_size")

    if not restaurant_id or not name or not party_size:
        return Response({"error": "Missing fields"}, status=400)

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    position = queue_length + 1

    Queue.objects.create(
        restaurant=restaurant,
        name=name,
        party_size=party_size,
        position=position,
        status="waiting"
    )

    update_queue_positions(restaurant)

    wait_time = get_safe_wait_time(restaurant)

    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time,
        queue_length=queue_length + 1,
        occupied_tables=restaurant.occupied_tables,
        total_tables=restaurant.total_tables
    )

    send_realtime_update(restaurant, "update", wait_time)

    return Response({
        "status": "waiting",
        "position": position,
        "estimated_wait": round(wait_time)
    })

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def leave_queue(request):
    restaurant_id = request.data.get("restaurant")
    name = request.data.get("name")

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    entry = Queue.objects.filter(
        restaurant=restaurant,
        name=name
    ).first()

    if not entry:
        return Response({"error": "User not found"}, status=404)

    # if seated → free table
    if entry.status == "seated":
        table = Table.objects.filter(
            restaurant=restaurant,
            status="OCCUPIED"
        ).first()

        if table:
            table.status = "FREE"
            table.save()

    entry.status = "left"
    entry.save()

    # CRITICAL
    process_queue(restaurant)

    wait_time = get_safe_wait_time(restaurant)

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"status": "left"})

@api_view(['GET'])
def predict_wait(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    update_queue_positions(restaurant)
    sync_restaurant_tables(restaurant)

    wait_time = calculate_wait_time(restaurant)

    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    # 🔥 NEVER allow unrealistic wait if queue exists
    if queue_length > 0:
         wait_time = max(5, round(wait_time))
    else:
        wait_time = max(0, round(wait_time))

    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    confidence = random.randint(80, 95)

    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time,
        queue_length=queue_length,
        occupied_tables=restaurant.occupied_tables,
        total_tables=restaurant.total_tables,
        confidence=confidence
    )

    return Response({
        "wait_time": wait_time,
        "confidence": confidence,
        "position": queue_length
})

@api_view(['GET'])
def recommend_restaurants(request):
    restaurants = Restaurant.objects.all()

    results = []

    for r in restaurants:
        wait = calculate_wait_time(r)

        score = (-wait - r.occupied_tables * 2)

        results.append({
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "score": score,
            "wait_time": round(wait)
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return Response(results)


# ---------------- STAFF DASHBOARD ---------------- #

@api_view(['GET'])
def staff_dashboard(request, restaurant_id):

    if not request.user.is_authenticated:
        return Response({"error": "Not logged in"}, status=401)

    print("USER:", request.user)
    print("ROLE:", request.user.role)
    print("USER RESTAURANT:", request.user.restaurant)
    print("USER RESTAURANT ID:", getattr(request.user.restaurant, "id", None))
    print("URL ID:", restaurant_id)

    # 🔐 ROLE CHECK
    if request.user.role != "staff":
        return Response({"error": "Unauthorized"}, status=403)

    # 🔐 USER MUST HAVE RESTAURANT
    if not request.user.restaurant:
        return Response({"error": "No restaurant assigned"}, status=403)

    # 🔐 MUST MATCH RESTAURANT ID
    if request.user.restaurant.id != int(restaurant_id):
        return Response({"error": "Wrong restaurant"}, status=403)

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    tables = Table.objects.filter(restaurant=restaurant)

    # 🔥 FIX: ensure positions are correct BEFORE sending to frontend
    update_queue_positions(restaurant)

    queue = Queue.objects.filter(
    restaurant=restaurant,
    status="waiting"
    ).order_by("joined_at")

    sync_restaurant_tables(restaurant)

    occupied = restaurant.occupied_tables
    free = restaurant.total_tables - occupied

    queue_count = Queue.objects.filter(
    restaurant=restaurant,
    status="waiting"
).count()

    wait_time = calculate_wait_time(restaurant)

    if queue_count > 0:
        wait_time = max(5, round(wait_time))
    else:
        wait_time = max(0, round(wait_time))

    return Response({
        "restaurant": restaurant.name,
        "tables": TableSerializer(tables, many=True).data,
        "queue": QueueSerializer(queue, many=True).data,
        "occupied_tables": occupied,
        "free_tables": free,
        "wait_time": wait_time
    })

# ---------------- TABLE UPDATE ---------------- #

@api_view(['PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication, BasicAuthentication])
@permission_classes([AllowAny])
def update_table_status(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    new_status = request.data.get("status")

    if new_status not in ["FREE", "OCCUPIED", "RESERVED"]:
        return Response({"error": "Invalid status"}, status=400)

    table.status = new_status.upper()
    table.save()

    restaurant = table.restaurant
    sync_restaurant_tables(restaurant)

    wait_time = get_safe_wait_time(restaurant)

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

    send_realtime_update(restaurant, "update", wait_time)

    return Response({
    "message": "Table updated",
    "status": table.status,
    "wait_time": wait_time
})


# ---------------- BILLING ---------------- #

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def billing_complete(request):
    table_id = request.data.get("table_id")

    table = get_object_or_404(Table, id=table_id)

    table.status = "FREE"
    table.save()

    restaurant = table.restaurant
    sync_restaurant_tables(restaurant)

    process_queue(restaurant)

    wait_time = get_safe_wait_time(restaurant)

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

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"message": "Billing simulated"})

# ---------------- SEAT CUSTOMER ---------------- #

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def seat_customer(request):
    queue_id = request.data.get("queue_id")

    entry = get_object_or_404(Queue, id=queue_id)

    restaurant = entry.restaurant

    # mark seated
    entry.status = "seated"
    entry.position = None
    entry.save()

    # free one table OR mark occupied (your logic choice)
    table = Table.objects.filter(
        restaurant=restaurant,
        status="FREE"
    ).first()

    if table:
        table.status = "OCCUPIED"
        table.save()

    update_queue_positions(restaurant)
    sync_restaurant_tables(restaurant)

    wait_time = get_safe_wait_time(restaurant)

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
    next_customer = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting",
        position=1
    ).first()

    if next_customer:
         print("🔔 Customer ready!")

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"message": "Customer seated"})