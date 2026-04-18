from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import random



class ModelMetrics(models.Model):
    mae = models.FloatField()
    rmse = models.FloatField()
    r2 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class User(AbstractUser):
    role = models.CharField(max_length=20, default="customer")

    restaurant = models.ForeignKey(
        "Restaurant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

class PasswordResetOTP(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # valid for 10 minutes
        return timezone.now() < self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    capacity = models.IntegerField(default=20)

    # ADD THESE
    total_tables = models.IntegerField(default=10)
    occupied_tables = models.IntegerField(default=5)
    avg_dining_time = models.IntegerField(default=30)  # minutes
    lat = models.FloatField(default=51.5074)  # London fallback
    lng = models.FloatField(default=-0.1278)

    menu_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    seats = models.IntegerField(default=4)

    table_number = models.IntegerField(default=1)

    STATUS_CHOICES = [
        ('FREE', 'Free'),
        ('OCCUPIED', 'Occupied'),
        ('RESERVED', 'Reserved'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='FREE'
    )

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.table_number} ({self.status})"
    
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    threshold = models.IntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.restaurant.name} ({self.threshold} mins)"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"
    

@receiver(post_save, sender=Restaurant)
def create_tables_for_new_restaurant(sender, instance, created, **kwargs):
    if created:
        for i in range(1, 11):
            Table.objects.create(
                restaurant=instance,
                table_number=i,
                status="FREE",
                seats=4
            )


class Prediction(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    wait_time = models.FloatField()

    # 🔥 ML features
    queue_length = models.IntegerField()
    occupied_tables = models.IntegerField()
    total_tables = models.IntegerField()   
    confidence = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    party_size = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.wait_time} mins"
    


class Queue(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("seated", "Seated"),
        ("left", "Left"),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    party_size = models.IntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="waiting"
    )

    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

    class Meta:
        ordering = ["joined_at"]

class OccupancyLog(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    occupied_tables = models.IntegerField()
    total_tables = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.occupied_tables}/{self.total_tables}"
    
class BillingEvent(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Billing - {self.table}"