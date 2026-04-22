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
from .train_model import train
from .utils import calculate_wait_time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .permissions import IsStaffUser, IsCustomerUser
import logging
logger = logging.getLogger(__name__)
from .models import Subscription, Notification
from .serializers import NotificationSerializer
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP


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
    serializer_class = QueueSerializer

    def get_queryset(self):
        return Queue.objects.filter(status__in=["waiting", "seated"])

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

# ---------------- HELPER FUNCTIONS ---------------- #

def check_and_send_notifications(restaurant, wait_time):
    subscriptions = Subscription.objects.filter(restaurant=restaurant)

    for sub in subscriptions:

        # WAIT TIME ALERT (prevent spam)
        already_sent_wait = Notification.objects.filter(
            user=sub.user,
            restaurant=restaurant,
            message__icontains="wait time"
        ).exists()

        if wait_time <= sub.threshold and not already_sent_wait:
            Notification.objects.create(
                user=sub.user,
                restaurant=restaurant,
                message=f"⏰ {restaurant.name} wait time is now {wait_time} mins!"
            )

        # TABLE READY ALERT (prevent spam)
        user_queue = Queue.objects.filter(
            restaurant=restaurant,
            name=sub.user.username,
            status__in=["waiting", "seated"]
        ).first()

        if user_queue:
            already_sent_table = Notification.objects.filter(
                user=sub.user,
                restaurant=restaurant,
                message__icontains="table"
            ).exists()

            if (user_queue.status == "seated" or user_queue.position == 1) and not already_sent_table:
                Notification.objects.create(
                    user=sub.user,
                    restaurant=restaurant,
                    message=f"🎉 Your table at {restaurant.name} is ready!"
                )

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
    result = calculate_wait_time(restaurant)

    wait_time = result["wait_time"]   # exact wait time from model

    queue_count = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

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

def maybe_retrain_model():
    try:
        count = Prediction.objects.count()

        # trigger every 10 new records
        if count >= 10 and count % 20 == 0:
            logger.info(f"Auto-training triggered at {count} records")
            train()
    except Exception as e:
        logger.error(f"Retraining error: {e}")

# ---------------- API FUNCTIONS ---------------- #

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get("email")
    password = request.data.get("password")
    name = request.data.get("name")   
    role = request.data.get("role", "customer")

    if not email or not password:
        return Response({"error": "Missing fields"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "User already exists"}, status=400)

    # Create user 
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )

    
    user.first_name = name
    user.role = role
    user.save()

    return Response({"message": "User created"})

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    email = request.data.get("email")

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=404)

    otp = str(random.randint(100000, 999999))

    PasswordResetOTP.objects.create(user=user, otp=otp)

    send_mail(
        "SmartWait Password Reset OTP",
        f"Your OTP is: {otp}",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    return Response({"message": "OTP sent"})

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    new_password = request.data.get("password")

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=404)

    record = PasswordResetOTP.objects.filter(user=user, otp=otp).last()

    if not record or not record.is_valid():
        return Response({"error": "Invalid or expired OTP"}, status=400)

    user.set_password(new_password)
    user.save()

    record.delete()  # cleanup

    return Response({"message": "Password reset successful"})

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Missing credentials"}, status=400)

    user = User.objects.filter(email=email).first()

    if not user:
        return Response({"error": "Invalid credentials"}, status=400)

    # AUTHENTICATE USING USERNAME
    authenticated_user = authenticate(
        request,
        username=user.username,
        password=password
    )

    if authenticated_user is not None:
        login(request, authenticated_user)

        return Response({
            "message": "Logged in",
            "role": authenticated_user.role,
            "restaurant_id": authenticated_user.restaurant.id if authenticated_user.restaurant else None
        })

    return Response({"error": "Invalid credentials"}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out"})


@api_view(['POST'])
def forgot_password(request):
    email = request.data.get("email")

    user = User.objects.filter(email=email).first()

    if user:
        user.set_password("newpassword123")  # simulate reset
        user.save()

    return Response({"message": "Password reset (simulated)"})

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def simulate_rush(request):
    restaurant_id = request.data.get("restaurant")

    if not restaurant_id:
        return Response({"error": "Restaurant required"}, status=400)
    
    if request.user.role not in ["staff", "customer"]:
        return Response({"error": "Unauthorized role"}, status=403)

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    for i in range(5):
        Queue.objects.create(
            restaurant=restaurant,
            name=f"Rush {i}",
            party_size=random.randint(1, 5),
            status="waiting"
    )

    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=get_safe_wait_time(restaurant),
        queue_length=Queue.objects.filter(
            restaurant=restaurant,
            status="waiting"
        ).count(),
        occupied_tables=restaurant.occupied_tables,
        total_tables=restaurant.total_tables,
    )

    update_queue_positions(restaurant)

    wait_time = get_safe_wait_time(restaurant)
    check_and_send_notifications(restaurant, wait_time)

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"message": "Rush simulated"})

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated, IsCustomerUser])
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
    check_and_send_notifications(restaurant, wait_time)

    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time,
        queue_length=queue_length + 1,
        occupied_tables=restaurant.occupied_tables,
        total_tables=restaurant.total_tables,
    )
    maybe_retrain_model()

    send_realtime_update(restaurant, "update", wait_time)

    return Response({
        "status": "waiting",
        "position": position,
        "estimated_wait": round(wait_time)
    })

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated, IsCustomerUser])
def leave_queue(request):
    restaurant_id = request.data.get("restaurant")
    name = request.data.get("name")

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    entry = Queue.objects.filter(
        restaurant=restaurant,
        name=name,
        status__in=["waiting", "seated"]  # ✅ ONLY active entries
    ).first()

    if not entry:
        return Response({"error": "User not found"}, status=404)

    # free table if seated
    if entry.status == "seated":
        table = Table.objects.filter(
            restaurant=restaurant,
            status="OCCUPIED"
        ).first()

        if table:
            table.status = "FREE"
            table.save()

    entry.delete()

    process_queue(restaurant)

    wait_time = get_safe_wait_time(restaurant)
    check_and_send_notifications(restaurant, wait_time)
    maybe_retrain_model()

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"status": "left"})

@api_view(['GET'])
def predict_wait(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    update_queue_positions(restaurant)
    sync_restaurant_tables(restaurant)

    result = calculate_wait_time(restaurant)

    wait_time = result["wait_time"]
    used_ml = result["used_ml"]
    factors = result["factors"]

    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    # Never allow unrealistic wait if queue exists
    if queue_length > 0:
         wait_time = max(5, round(wait_time))
    else:
        wait_time = max(0, round(wait_time))

    queue_length = Queue.objects.filter(
        restaurant=restaurant,
        status="waiting"
    ).count()

    load_factor = factors["queue_length"] / max(1, factors["total_tables"])
    confidence = int(max(60, min(95, 95 - (load_factor * 20))))

    Prediction.objects.create(
        restaurant=restaurant,
        wait_time=wait_time,
        queue_length=queue_length,
        occupied_tables=restaurant.occupied_tables,
        total_tables=restaurant.total_tables,
        confidence=confidence
    )

    # AUTO RETRAIN EVERY 20 RECORDS
    maybe_retrain_model()

    # EXPLANATION ENGINE
    explanation = []

    if factors["queue_length"] > 10:
        explanation.append("High queue volume")

    if factors["occupied_tables"] / max(1, factors["total_tables"]) > 0.8:
        explanation.append("Restaurant nearly full")

    if factors["queue_length"] > factors["total_tables"]:
        explanation.append("Queue exceeds capacity")

    if not explanation:
        explanation.append("Low demand")

    return Response({
        "wait_time": wait_time,
        "confidence": confidence,
        "position": queue_length,
        "ml_used": used_ml,
        "factors": factors,
        "explanation": explanation
})

@api_view(['GET'])
def recommend_restaurants(request):
    restaurants = Restaurant.objects.all()

    results = []

    for r in restaurants:
        result = calculate_wait_time(r)
        wait = result["wait_time"]

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

    # ROLE CHECK
    if request.user.role != "staff":
        return Response({"error": "Unauthorized"}, status=403)

    # USER MUST HAVE RESTAURANT
    if not request.user.restaurant:
        return Response({"error": "No restaurant assigned"}, status=403)

    # MUST MATCH RESTAURANT ID
    if request.user.restaurant.id != int(restaurant_id):
        return Response({"error": "Wrong restaurant"}, status=403)

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    tables = Table.objects.filter(restaurant=restaurant)

    # update queue positions before sending data to ensure consistency
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

    result = calculate_wait_time(restaurant)
    wait_time = result["wait_time"] 

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def subscribe_alert(request):
    restaurant_id = request.data.get("restaurant")
    threshold = request.data.get("threshold", 5)
    if threshold < 1:
        threshold = 5

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    Subscription.objects.update_or_create(
        user=request.user,
        restaurant=restaurant,
        defaults={"threshold": threshold}
    )

    return Response({"message": "Subscribed for alerts"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    return Response(NotificationSerializer(notifications, many=True).data)

# ---------------- TABLE UPDATE ---------------- #

@api_view(['PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
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
    check_and_send_notifications(restaurant, wait_time)

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
    maybe_retrain_model()

    send_realtime_update(restaurant, "update", wait_time)

    return Response({
    "message": "Table updated",
    "status": table.status,
    "wait_time": wait_time
})


# ---------------- BILLING ---------------- #

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def billing_complete(request):
    table_id = request.data.get("table_id")

    table = get_object_or_404(Table, id=table_id)

    table.status = "FREE"
    table.save()

    restaurant = table.restaurant
    sync_restaurant_tables(restaurant)

    process_queue(restaurant)

    wait_time = get_safe_wait_time(restaurant)
    check_and_send_notifications(restaurant, wait_time)

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
    maybe_retrain_model()

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"message": "Billing simulated"})

# ---------------- SEAT CUSTOMER ---------------- #

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
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
    check_and_send_notifications(restaurant, wait_time)

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
    maybe_retrain_model()

    next_customer = Queue.objects.filter(
    restaurant=restaurant,
    status="waiting",
    position=1
).first()
    if next_customer:
        logger.info("Next customer ready")

    send_realtime_update(restaurant, "update", wait_time)

    return Response({"message": "Customer seated"})