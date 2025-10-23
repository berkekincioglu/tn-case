# Import routers from Django REST Framework
# Routers automatically generate URL patterns for ViewSets
from rest_framework.routers import DefaultRouter

# Import our viewset
from .views import AirplaneViewSet

# Create a router instance
# DefaultRouter automatically creates URL patterns for all ViewSet actions
# Think of it as a URL pattern generator that creates:
# - /airplanes/ -> list() and create()
# - /airplanes/{id}/ -> retrieve(), update(), partial_update(), destroy()
# - /airplanes/{id}/flights/ -> flights() custom action
router = DefaultRouter()

# Register the viewset with the router
# Parameters:
# - 'airplanes': URL prefix (all URLs will start with /airplanes/)
# - AirplaneViewSet: The viewset to generate URLs for
# - basename='airplane': Optional name for URL patterns
router.register(r'airplanes', AirplaneViewSet, basename='airplane')

# Export the URL patterns
# router.urls generates a list of URL patterns based on the registered viewsets
urlpatterns = router.urls
