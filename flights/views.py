from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Flight
from .serializers import FlightSerializer, FlightListSerializer
from reservations.serializers import ReservationListSerializer
from datetime import datetime


class FlightViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing flights.

    Supports filtering by departure, destination, and dates.
    Provides custom action to retrieve flight reservations.
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        """Apply filters based on query parameters."""
        queryset = Flight.objects.select_related('airplane').all()

        # Filter by departure location
        departure = self.request.query_params.get('departure')
        if departure:
            queryset = queryset.filter(departure__icontains=departure)

        # Filter by destination location
        destination = self.request.query_params.get('destination')
        if destination:
            queryset = queryset.filter(destination__icontains=destination)

        # Filter by departure date
        departure_date = self.request.query_params.get('departure_date')
        if departure_date:
            try:
                date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_time__date=date_obj)
            except ValueError:
                pass  # Invalid date format, skip filtering

        # Filter by arrival date
        arrival_date = self.request.query_params.get('arrival_date')
        if arrival_date:
            try:
                date_obj = datetime.strptime(arrival_date, '%Y-%m-%d').date()
                queryset = queryset.filter(arrival_time__date=date_obj)
            except ValueError:
                pass  # Invalid date format, skip filtering

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return FlightListSerializer
        return FlightSerializer

    @action(detail=True, methods=['get'], url_path='reservations')
    def reservations(self, request, pk=None):
        """Get all reservations for this flight (with pagination)."""
        flight = self.get_object()
        queryset = flight.reservations.all()

        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param is not None:
            is_active = status_param.lower() == 'true'
            queryset = queryset.filter(status=is_active)

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReservationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback if pagination is not configured
        serializer = ReservationListSerializer(queryset, many=True)
        return Response(serializer.data)
