"""
URL configuration for airline_project project.

This file defines the main URL routing for the entire project.
It includes all app URLs and additional features like admin and API documentation.
"""

# Import Django's admin interface
from django.contrib import admin

# Import path and include functions for URL routing
# - path(): Creates a URL pattern
# - include(): Includes URL patterns from other files
from django.urls import path, include

# Import drf-spectacular views for API documentation
# These provide Swagger/OpenAPI documentation for your API
from drf_spectacular.views import (
    SpectacularAPIView,  # Generates OpenAPI schema
    SpectacularRedocView,  # ReDoc documentation UI
    SpectacularSwaggerView,  # Swagger UI documentation
)

# Define URL patterns
# urlpatterns is a list of URL patterns that Django will try to match
# Django checks these patterns in order from top to bottom
urlpatterns = [
    # Django Admin Interface
    # URL: /admin/
    # This provides a web interface for managing your database
    path('admin/', admin.site.urls),

    # API Documentation URLs (using drf-spectacular)
    # These provide interactive documentation for testing your API

    # OpenAPI Schema (JSON format)
    # URL: /api/schema/
    # This returns the API specification in OpenAPI format
    # You can download this file and import it into Postman
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI Documentation
    # URL: /api/docs/
    # This provides an interactive web interface for testing your API
    # You can see all endpoints and try them directly from your browser
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc Documentation (alternative UI)
    # URL: /api/redoc/
    # Another documentation interface with a different style
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Endpoints
    # include(): Includes all URL patterns from the specified app
    # This imports all the URLs we defined in each app's urls.py file

    # Airplane API endpoints
    # URL: /api/airplanes/...
    # Includes: /api/airplanes/, /api/airplanes/{id}/, /api/airplanes/{id}/flights/
    path('api/', include('airplanes.urls')),

    # Flight API endpoints
    # URL: /api/flights/...
    # Includes: /api/flights/, /api/flights/{id}/, /api/flights/{id}/reservations/
    path('api/', include('flights.urls')),

    # Reservation API endpoints
    # URL: /api/reservations/...
    # Includes: /api/reservations/, /api/reservations/{id}/, /api/reservations/{id}/cancel/
    path('api/', include('reservations.urls')),
]

"""
Summary of all available endpoints:

AIRPLANES:
- GET    /api/airplanes/              - List all airplanes
- POST   /api/airplanes/              - Create new airplane
- GET    /api/airplanes/{id}/         - Get airplane details
- PATCH  /api/airplanes/{id}/         - Update airplane
- DELETE /api/airplanes/{id}/         - Delete airplane
- GET    /api/airplanes/{id}/flights/ - Get flights for airplane

FLIGHTS:
- GET    /api/flights/                    - List all flights (supports filtering)
- POST   /api/flights/                    - Create new flight
- GET    /api/flights/{id}/               - Get flight details
- PATCH  /api/flights/{id}/               - Update flight
- DELETE /api/flights/{id}/               - Delete flight
- GET    /api/flights/{id}/reservations/  - Get reservations for flight

RESERVATIONS:
- GET    /api/reservations/            - List all reservations
- POST   /api/reservations/            - Create new reservation
- GET    /api/reservations/{id}/       - Get reservation details
- PATCH  /api/reservations/{id}/       - Update reservation
- POST   /api/reservations/{id}/cancel/ - Cancel reservation

DOCUMENTATION:
- GET    /api/schema/                  - OpenAPI schema (JSON)
- GET    /api/docs/                    - Swagger UI
- GET    /api/redoc/                   - ReDoc UI
- GET    /admin/                       - Django Admin
"""
