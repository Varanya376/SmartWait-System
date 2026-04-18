from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import *
from django.contrib import admin

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'tables', TableViewSet)
router.register(r'queue', QueueViewSet)
router.register(r'predictions', PredictionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # AUTH
    path("api/register/", register),
    path("api/login/", login_view),
    path("api/logout/", logout_view),
    path("api/forgot/", forgot_password),
    path("api/send_otp/", send_otp),
    path("api/verify_otp/", verify_otp),

    # CORE FEATURES
    path("api/predict-wait/<int:restaurant_id>/", predict_wait),
    path("api/join_queue/", join_queue),
    path("api/leave_queue/", leave_queue),
    path("api/simulate_rush/", simulate_rush),
    path("api/subscribe_alert/", subscribe_alert),
    path("api/notifications/", get_notifications),

    # STAFF
    path("api/staff/<int:restaurant_id>/", staff_dashboard),
]