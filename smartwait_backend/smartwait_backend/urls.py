from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import RestaurantViewSet, TableViewSet, PredictionViewSet, QueueViewSet, join_queue, leave_queue, predict_wait
from api.views import recommend_restaurants


router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'tables', TableViewSet)
router.register(r'predictions', PredictionViewSet)
router.register(r'queue', QueueViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/join_queue/', join_queue),
    path('api/leave_queue/', leave_queue),
    path("api/predict-wait/<int:restaurant_id>/", predict_wait),
    path("api/recommend/", recommend_restaurants),
]