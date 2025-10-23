from django.db import models


class Airplane(models.Model):
    """Airplane model representing an aircraft in the airline's fleet."""

    tail_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique aircraft registration number (e.g., TC-NRT)"
    )

    model = models.CharField(
        max_length=100,
        help_text="Aircraft model (e.g., Airbus A320, Boeing 737)"
    )

    capacity = models.PositiveIntegerField(
        help_text="Maximum passenger capacity"
    )

    production_year = models.PositiveIntegerField(
        help_text="Year the aircraft was manufactured"
    )

    status = models.BooleanField(
        default=True,
        help_text="Aircraft operational status (True=Active, False=Inactive)"
    )

    class Meta:
        ordering = ['-production_year', 'tail_number']
        verbose_name = "Airplane"
        verbose_name_plural = "Airplanes"

    def __str__(self):
        return f"{self.tail_number} ({self.model})"

    def is_operational(self):
        """Check if airplane is operational."""
        return self.status
