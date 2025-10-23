from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Reservation
from .serializers import (
    ReservationSerializer,
    ReservationListSerializer,
    ReservationCreateSerializer
)
from .emails import send_reservation_confirmation_email, send_cancellation_email
import logging

logger = logging.getLogger(__name__)


class ReservationViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet for managing reservations.

    Uses mixins for selective CRUD operations (no DELETE).
    Reservations should be cancelled, not deleted, for record-keeping.
    """
    queryset = Reservation.objects.select_related('flight', 'flight__airplane').all()
    serializer_class = ReservationSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ReservationCreateSerializer
        elif self.action == 'list':
            return ReservationListSerializer
        return ReservationSerializer

    def get_queryset(self):
        """Apply filters based on query parameters."""
        queryset = super().get_queryset()

        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param is not None:
            is_active = status_param.lower() == 'true'
            queryset = queryset.filter(status=is_active)

        # Filter by flight
        flight_id = self.request.query_params.get('flight')
        if flight_id:
            queryset = queryset.filter(flight_id=flight_id)

        # Filter by passenger email
        email = self.request.query_params.get('passenger_email')
        if email:
            queryset = queryset.filter(passenger_email__iexact=email)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create reservation and send confirmation email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Get full reservation details
        reservation = Reservation.objects.select_related('flight', 'flight__airplane').get(
            id=serializer.instance.id
        )

        # Send confirmation email
        email_sent = send_reservation_confirmation_email(reservation)

        # Prepare response
        response_serializer = ReservationListSerializer(reservation)
        response_data = response_serializer.data
        response_data['email_sent'] = email_sent
        response_data['message'] = 'Reservation created successfully!'

        if not email_sent:
            response_data['email_message'] = 'Reservation created but email could not be sent'

        logger.info(f'Reservation created: {reservation.reservation_code}')
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel reservation and send cancellation email."""
        reservation = self.get_object()

        if not reservation.status:
            return Response(
                {'error': 'Reservation is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get flight info before cancellation
        flight = reservation.flight

        # Cancel the reservation
        reservation.cancel()
        email_sent = send_cancellation_email(reservation)

        logger.info(f'Reservation cancelled: {reservation.reservation_code}')

        # Return updated flight availability info
        return Response({
            'message': 'Reservation cancelled successfully.',
            'reservation_code': reservation.reservation_code,
            'email_sent': email_sent,
            'flight_info': {
                'flight_number': flight.flight_number,
                'available_seats': flight.available_seats(),
                'total_capacity': flight.airplane.capacity,
                'active_reservations': flight.get_reservation_count(),
                'is_fully_booked': flight.is_fully_booked()
            }
        })
