from rest_framework import serializers
from .models import Restaurant, Table, Prediction, Queue
from .utils import calculate_wait_time
from .models import Subscription, Notification

class RestaurantSerializer(serializers.ModelSerializer):
    wait_time = serializers.SerializerMethodField()
    live_occupied_tables = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = "__all__"

    def get_wait_time(self, obj):
        return calculate_wait_time(obj)

    def get_live_occupied_tables(self, obj):
        return obj.table_set.filter(status="OCCUPIED").count()

class TableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Table
        fields = '__all__'


class PredictionSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Prediction
        fields = '__all__'

class QueueSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Queue
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

class StaffDashboardSerializer(serializers.Serializer):
    restaurant = serializers.CharField()
    tables = TableSerializer(many=True)
    occupied_tables = serializers.IntegerField()
    free_tables = serializers.IntegerField()
    wait_time = serializers.FloatField()

ASGI_APPLICATION = "smartwait_backend.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}