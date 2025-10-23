from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta


class Flight(models.Model):
    """Flight model representing a scheduled flight from one location to another."""

    flight_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique flight identifier (e.g., TK123, BA456)"
    )

    departure = models.CharField(
        max_length=200,
        help_text="Departure airport or location"
    )

    destination = models.CharField(
        max_length=200,
        help_text="Destination airport or location"
    )

    departure_time = models.DateTimeField(
        help_text="Date and time when the flight departs"
    )

    arrival_time = models.DateTimeField(
        help_text="Date and time when the flight arrives"
    )

    airplane = models.ForeignKey(
        'airplanes.Airplane',
        on_delete=models.CASCADE,
        related_name='flights',
        help_text="The airplane assigned to this flight"
    )

    class Meta:
        ordering = ['departure_time']
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        constraints = [
            models.CheckConstraint(
                check=models.Q(arrival_time__gt=models.F('departure_time')),
                name='arrival_after_departure'
            )
        ]

    def __str__(self):
        return f"{self.flight_number}: {self.departure} → {self.destination}"

    def clean(self):
        """Validate flight data and check for conflicts."""
        super().clean()

        # Ensure arrival time is after departure time
        if self.arrival_time and self.departure_time:
            if self.arrival_time <= self.departure_time:
                raise ValidationError({
                    'arrival_time': 'Arrival time must be after departure time.'
                })

        # Check for flight conflicts with the same airplane
        if self.airplane_id:
            self._check_flight_conflicts()

    def _check_flight_conflicts(self):
        """
        Check for flight time conflicts with the same airplane.

        Business Rule: An airplane must have at least 1 hour gap between flights
        to allow for passenger boarding/disembarking, cleaning, and maintenance.
        """
        buffer_time = timedelta(hours=1)
        conflict_start = self.departure_time - buffer_time
        conflict_end = self.arrival_time + buffer_time

        # Find overlapping flights for the same airplane
        conflicting_flights = Flight.objects.filter(
            airplane=self.airplane
        ).exclude(
            id=self.id  # Exclude this flight when updating
        ).filter(
            models.Q(departure_time__range=(conflict_start, conflict_end)) |
            models.Q(arrival_time__range=(conflict_start, conflict_end)) |
            models.Q(departure_time__lte=conflict_start, arrival_time__gte=conflict_end)
        )

        if conflicting_flights.exists():
            conflict = conflicting_flights.first()
            raise ValidationError({
                'airplane': f'This airplane is already scheduled for flight {conflict.flight_number} '
                           f'from {conflict.departure_time} to {conflict.arrival_time}. '
                           f'Flights must have at least 1 hour gap between them.'
            })

    def save(self, *args, **kwargs):
        """Ensure validation runs before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_reservation_count(self):
        """Return the number of reservations for this flight."""
        return self.reservations.filter(status=True).count()

    def is_fully_booked(self):
        """Check if flight has reached maximum capacity."""
        return self.get_reservation_count() >= self.airplane.capacity

    def available_seats(self):
        """Return number of available seats on this flight."""
        return self.airplane.capacity - self.get_reservation_count()
