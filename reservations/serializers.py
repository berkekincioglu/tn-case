from rest_framework import serializers
from .models import Reservation
from flights.models import Flight
from flights.serializers import FlightListSerializer


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservation model with nested flight details."""
    reservation_code = serializers.CharField(read_only=True)
    flight_details = serializers.SerializerMethodField(read_only=True)
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id',
            'passenger_name',
            'passenger_email',
            'reservation_code',
            'flight',
            'flight_details',
            'status',
            'status_display',
            'created_at',
        ]
        read_only_fields = ['id', 'reservation_code', 'flight_details', 'status_display', 'created_at']

    def get_flight_details(self, obj):
        """Return detailed flight information."""
        flight = obj.flight
        return {
            'id': flight.id,
            'flight_number': flight.flight_number,
            'departure': flight.departure,
            'destination': flight.destination,
            'departure_time': flight.departure_time,
            'arrival_time': flight.arrival_time,
            'airplane': {
                'tail_number': flight.airplane.tail_number,
                'model': flight.airplane.model,
            }
        }

    def get_status_display(self, obj):
        """Return human-readable status."""
        return 'Active' if obj.status else 'Cancelled'

    def validate_passenger_name(self, value):
        """Validate passenger name is not empty."""
        value = value.strip()
        if not value or len(value) < 2:
            raise serializers.ValidationError("Passenger name must be at least 2 characters.")
        return value

    def validate_passenger_email(self, value):
        """Validate and normalize passenger email."""
        return value.lower().strip()

    def validate(self, data):
        """Validate no duplicate email on the same flight when updating."""
        # Get the flight (from data if being updated, or from instance if not)
        flight = data.get('flight', self.instance.flight if self.instance else None)
        passenger_email = data.get('passenger_email', self.instance.passenger_email if self.instance else None)

        if flight and passenger_email:
            # Check if this email already has an active reservation for this flight
            duplicate_check = Reservation.objects.filter(
                flight=flight,
                passenger_email__iexact=passenger_email,
                status=True
            )

            # Exclude current reservation when updating
            if self.instance:
                duplicate_check = duplicate_check.exclude(pk=self.instance.pk)

            if duplicate_check.exists():
                raise serializers.ValidationError(
                    f"An active reservation already exists for {passenger_email} on flight {flight.flight_number}."
                )

        return data


class ReservationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing reservations."""
    flight = FlightListSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            'id',
            'reservation_code',
            'passenger_name',
            'passenger_email',
            'flight',
            'status',
            'status_display',
            'created_at',
        ]

    def get_status_display(self, obj):
        """Return human-readable status."""
        return 'Active' if obj.status else 'Cancelled'


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reservations."""
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())

    class Meta:
        model = Reservation
        fields = ['passenger_name', 'passenger_email', 'flight']

    def validate_passenger_name(self, value):
        """Validate passenger name."""
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Passenger name must be at least 2 characters.")
        return value

    def validate_passenger_email(self, value):
        """Validate and normalize email."""
        return value.lower().strip()

    def validate(self, data):
        """Validate flight capacity, departure time, and duplicate email."""
        flight = data.get('flight')
        passenger_email = data.get('passenger_email')

        # Check if flight has departed
        from django.utils import timezone
        if flight.departure_time < timezone.now():
            raise serializers.ValidationError("Cannot book a flight that has already departed.")

        # Check if this email already has an active reservation for this flight
        existing_reservation = Reservation.objects.filter(
            flight=flight,
            passenger_email__iexact=passenger_email,
            status=True
        ).exists()

        if existing_reservation:
            raise serializers.ValidationError(
                f"An active reservation already exists for {passenger_email} on flight {flight.flight_number}."
            )

        # Check capacity
        active_reservations = Reservation.objects.filter(flight=flight, status=True).count()
        if active_reservations >= flight.airplane.capacity:
            raise serializers.ValidationError(
                f"Flight {flight.flight_number} is fully booked. "
                f"Capacity: {flight.airplane.capacity}"
            )

        return data
