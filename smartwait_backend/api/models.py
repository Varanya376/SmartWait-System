from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50) 

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
    
from django.db import models

class Queue(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    party_size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"