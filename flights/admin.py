from django.contrib import admin
from .models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """Custom admin interface for Flight model."""

    list_display = [
        'id',
        'flight_number',
        'departure',
        'destination',
        'departure_time',
        'arrival_time',
        'get_airplane_info',
        'get_available_seats',
    ]

    list_filter = ['departure_time', 'departure', 'destination', 'airplane']
    search_fields = ['flight_number', 'departure', 'destination', 'airplane__tail_number']
    ordering = ['departure_time']
    readonly_fields = ['id']

    fieldsets = (
        ('Flight Information', {
            'fields': ('flight_number', 'airplane')
        }),
        ('Route', {
            'fields': ('departure', 'destination')
        }),
        ('Schedule', {
            'fields': ('departure_time', 'arrival_time')
        }),
    )

    def get_airplane_info(self, obj):
        """Return airplane tail number and model."""
        return f"{obj.airplane.tail_number} ({obj.airplane.model})"
    get_airplane_info.short_description = 'Airplane'

    def get_available_seats(self, obj):
        """Return available seats / total capacity."""
        return f"{obj.available_seats()} / {obj.airplane.capacity}"
    get_available_seats.short_description = 'Available Seats'
