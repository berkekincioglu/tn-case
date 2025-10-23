from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import string
import secrets


class Reservation(models.Model):
    """Reservation model representing a passenger's flight booking."""

    passenger_name = models.CharField(
        max_length=200,
        help_text="Full name of the passenger"
    )

    passenger_email = models.EmailField(
        max_length=254,
        help_text="Email address for confirmation"
    )

    reservation_code = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        blank=True,
        help_text="Auto-generated unique reservation code"
    )

    flight = models.ForeignKey(
        'flights.Flight',
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="The flight this reservation is for"
    )

    status = models.BooleanField(
        default=True,
        help_text="Reservation status (True=Active, False=Cancelled)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when reservation was created"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        indexes = [
            models.Index(fields=['reservation_code']),
            models.Index(fields=['passenger_email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.reservation_code} - {self.passenger_name}"

    @staticmethod
    def _generate_reservation_code():
        """Generate a unique 8-character alphanumeric reservation code."""
        characters = string.ascii_uppercase + string.digits

        while True:
            code = ''.join(secrets.choice(characters) for _ in range(8))
            if not Reservation.objects.filter(reservation_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        """Auto-generate reservation code before saving."""
        if not self.pk and not self.reservation_code:
            self.reservation_code = self._generate_reservation_code()

        super().save(*args, **kwargs)

    def clean(self):
        """Validate reservation data."""
        super().clean()

        # Check if flight has departed
        if self.flight.departure_time < timezone.now():
            raise ValidationError("Cannot book a flight that has already departed.")

        # Check if this email already has an active reservation for this flight
        duplicate_check = Reservation.objects.filter(
            flight=self.flight,
            passenger_email__iexact=self.passenger_email,
            status=True
        )

        # Exclude current reservation when updating
        if self.pk:
            duplicate_check = duplicate_check.exclude(pk=self.pk)

        if duplicate_check.exists():
            raise ValidationError(
                f"An active reservation already exists for {self.passenger_email} on flight {self.flight.flight_number}."
            )

        # Check if flight has available capacity
        active_reservations = Reservation.objects.filter(
            flight=self.flight,
            status=True
        ).count()

        # Exclude current reservation when updating
        if self.pk:
            try:
                current = Reservation.objects.get(pk=self.pk)
                if current.status:
                    active_reservations -= 1
            except Reservation.DoesNotExist:
                pass

        if active_reservations >= self.flight.airplane.capacity:
            raise ValidationError(
                f"Flight {self.flight.flight_number} is fully booked. "
                f"Capacity: {self.flight.airplane.capacity}"
            )

    def cancel(self):
        """Cancel this reservation (soft delete)."""
        self.status = False
        self.save(update_fields=['status'])  # Only update status field, skip validation

    def is_active(self):
        """Check if reservation is active."""
        return self.status
