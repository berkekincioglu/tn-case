from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from .models import Airplane
from .serializers import AirplaneSerializer, AirplaneListSerializer
from flights.serializers import FlightListSerializer
import logging

logger = logging.getLogger(__name__)


class AirplaneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing airplanes.

    Provides CRUD operations and custom actions for airplane management.
    """
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_queryset(self):
        """Filter airplanes by status if provided in query params."""
        queryset = Airplane.objects.all()

        status_param = self.request.query_params.get('status')
        if status_param is not None:
            is_active = status_param.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(status=is_active)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return AirplaneListSerializer
        return AirplaneSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Delete airplane if it has no associated flights.

        Prevents deletion of airplanes that have flights assigned to maintain data integrity.
        """
        instance = self.get_object()

        if instance.flights.exists():
            return Response(
                {
                    'error': f'Cannot delete airplane {instance.tail_number}. '
                            f'It has {instance.flights.count()} associated flights.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        logger.info(f'Airplane deleted: {instance.tail_number}')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='flights')
    def flights(self, request, pk=None):
        """Get all flights assigned to this airplane (with pagination)."""
        airplane = self.get_object()
        flights = airplane.flights.all()

        # Apply pagination
        page = self.paginate_queryset(flights)
        if page is not None:
            serializer = FlightListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        # Fallback if pagination is not configured
        serializer = FlightListSerializer(flights, many=True, context={'request': request})
        return Response(serializer.data)
