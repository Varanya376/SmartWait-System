from django.contrib import admin
from .models import Restaurant, Table, Prediction, Queue
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.register(Restaurant)
admin.site.register(Table)
admin.site.register(Prediction)
admin.site.register(User)

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "position", "status")
