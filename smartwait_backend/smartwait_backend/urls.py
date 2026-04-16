from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    RestaurantViewSet, TableViewSet, PredictionViewSet, QueueViewSet,
    join_queue, leave_queue, predict_wait,
    recommend_restaurants,
    staff_dashboard,
    update_table_status,
    billing_complete,
    seat_customer
)

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'tables', TableViewSet)
router.register(r'predictions', PredictionViewSet)
router.register(r'queue', QueueViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ CUSTOM ROUTES FIRST (IMPORTANT)
    path('api/tables/update/<int:table_id>/', update_table_status),
    path('api/billing/complete/', billing_complete),
    path('api/seat/', seat_customer),
    path('api/staff/dashboard/<int:restaurant_id>/', staff_dashboard),

    # other APIs
    path('api/join_queue/', join_queue),
    path('api/leave_queue/', leave_queue),
    path("api/predict-wait/<int:restaurant_id>/", predict_wait),
    path("api/recommend/", recommend_restaurants),

    # ✅ FIXED (SEPARATE ROUTES)
    path('api/auth/', include('api.urls')),   # auth routes
    path('api/', include(router.urls)),       # viewsets
]