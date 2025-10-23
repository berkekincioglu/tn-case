from rest_framework import serializers
from .models import Flight
from airplanes.models import Airplane
from django.utils import timezone


class FlightSerializer(serializers.ModelSerializer):
    """
    Serializer for Flight model with nested airplane details and computed fields.
    """
    airplane_details = serializers.SerializerMethodField(read_only=True)
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())

    available_seats = serializers.SerializerMethodField(read_only=True)
    is_fully_booked = serializers.SerializerMethodField(read_only=True)
    reservation_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            'id',
            'flight_number',
            'departure',
            'destination',
            'departure_time',
            'arrival_time',
            'airplane',
            'airplane_details',
            'available_seats',
            'is_fully_booked',
            'reservation_count',
        ]
        read_only_fields = ['id', 'airplane_details', 'available_seats', 'is_fully_booked', 'reservation_count']

    def get_airplane_details(self, obj):
        """Return nested airplane information."""
        return {
            'id': obj.airplane.id,
            'tail_number': obj.airplane.tail_number,
            'model': obj.airplane.model,
            'capacity': obj.airplane.capacity,
        }

    def get_available_seats(self, obj):
        """Return number of available seats."""
        return obj.available_seats()

    def get_is_fully_booked(self, obj):
        """Return whether flight is fully booked."""
        return obj.is_fully_booked()

    def get_reservation_count(self, obj):
        """Return total reservations for this flight."""
        return obj.get_reservation_count()

    def validate_departure_time(self, value):
        """Validate departure time is in the future."""
        if value < timezone.now():
            raise serializers.ValidationError("Departure time must be in the future.")
        return value

    def validate(self, data):
        """Validate arrival time is after departure time and check for flight conflicts."""
        departure_time = data.get('departure_time', self.instance.departure_time if self.instance else None)
        arrival_time = data.get('arrival_time', self.instance.arrival_time if self.instance else None)
        airplane = data.get('airplane', self.instance.airplane if self.instance else None)

        # Validate arrival time is after departure time
        if departure_time and arrival_time:
            if arrival_time <= departure_time:
                raise serializers.ValidationError(
                    {"arrival_time": "Arrival time must be after departure time."}
                )

        # Check for flight conflicts with the same airplane
        if airplane and departure_time and arrival_time:
            from datetime import timedelta
            from django.db import models as django_models

            buffer_time = timedelta(hours=1)
            conflict_start = departure_time - buffer_time
            conflict_end = arrival_time + buffer_time

            # Find overlapping flights for the same airplane
            conflicting_flights = Flight.objects.filter(
                airplane=airplane
            )

            # Exclude current flight when updating
            if self.instance:
                conflicting_flights = conflicting_flights.exclude(id=self.instance.id)

            conflicting_flights = conflicting_flights.filter(
                django_models.Q(departure_time__range=(conflict_start, conflict_end)) |
                django_models.Q(arrival_time__range=(conflict_start, conflict_end)) |
                django_models.Q(departure_time__lte=conflict_start, arrival_time__gte=conflict_end)
            )

            if conflicting_flights.exists():
                conflict = conflicting_flights.first()
                raise serializers.ValidationError(
                    f"This airplane is already scheduled for flight {conflict.flight_number} "
                    f"from {conflict.departure_time} to {conflict.arrival_time}. "
                    f"Flights must have at least 1 hour gap between them."
                )

        return data


class FlightListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing flights."""
    airplane_model = serializers.CharField(source='airplane.model', read_only=True)
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            'id',
            'flight_number',
            'departure',
            'destination',
            'departure_time',
            'arrival_time',
            'airplane_model',
            'available_seats',
        ]

    def get_available_seats(self, obj):
        """Return available seats."""
        return obj.available_seats()
