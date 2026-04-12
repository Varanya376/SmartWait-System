from django.contrib import admin
from .models import Restaurant, Table, Prediction, Queue

admin.site.register(Restaurant)
admin.site.register(Table)
admin.site.register(Prediction)
admin.site.register(Queue)