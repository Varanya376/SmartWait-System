from django.contrib import admin
from .models import Restaurant, Table, Prediction, Queue

admin.site.register(Restaurant)
admin.site.register(Table)
admin.site.register(Prediction)

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "position", "status")