# Import routers from Django REST Framework
from rest_framework.routers import DefaultRouter

# Import our viewset
from .views import FlightViewSet

# Create a router instance
router = DefaultRouter()

# Register the FlightViewSet
# This automatically creates URL patterns:
# - GET /flights/ -> List all flights
# - POST /flights/ -> Create new flight
# - GET /flights/{id}/ -> Get flight details
# - PATCH /flights/{id}/ -> Update flight
# - DELETE /flights/{id}/ -> Delete flight
# - GET /flights/{id}/reservations/ -> Get reservations for flight (custom action)
router.register(r'flights', FlightViewSet, basename='flight')

# Export the URL patterns
urlpatterns = router.urls
