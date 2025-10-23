# Import routers from Django REST Framework
from rest_framework.routers import DefaultRouter

# Import our viewset
from .views import ReservationViewSet

# Create a router instance
router = DefaultRouter()

# Register the ReservationViewSet
# This automatically creates URL patterns:
# - GET /reservations/ -> List all reservations
# - POST /reservations/ -> Create new reservation
# - GET /reservations/{id}/ -> Get reservation details
# - PATCH /reservations/{id}/ -> Update reservation
# - POST /reservations/{id}/cancel/ -> Cancel reservation (custom action)
# Note: No DELETE operation since we excluded DestroyModelMixin
router.register(r'reservations', ReservationViewSet, basename='reservation')

# Export the URL patterns
urlpatterns = router.urls
