from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"restaurants", views.RestaurantViewSet)
router.register(r"tables", views.TableViewSet)
router.register(r'queue', views.QueueViewSet, basename='queue')

urlpatterns = [
    path("", include(router.urls)),

    path("register/", views.register),
    path("login/", views.login_view),
    path("logout/", views.logout_view),

    path("join_queue/", views.join_queue),
    path("leave_queue/", views.leave_queue),

    path("predict-wait/<int:restaurant_id>/", views.predict_wait),

    path("staff/<int:restaurant_id>/", views.staff_dashboard),

    path("billing/", views.billing_complete),

    path("seat/", views.seat_customer),  

    path("update_table_status/<int:table_id>/", views.update_table_status),
]