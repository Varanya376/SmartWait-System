from rest_framework import serializers
from .models import Restaurant, Table, Prediction, Queue
from .utils import calculate_wait_time

class RestaurantSerializer(serializers.ModelSerializer):
    wait_time = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = "__all__"

    def get_wait_time(self, obj):
        return calculate_wait_time(obj)

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'

class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = '__all__'