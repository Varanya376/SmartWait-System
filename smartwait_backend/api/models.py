from django.db import models

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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    seats = models.IntegerField()

    def __str__(self):
        return f"{self.restaurant.name} - {self.seats} seats"


class Prediction(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    wait_time = models.IntegerField()

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

    position = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

    class Meta:
        ordering = ["joined_at"]