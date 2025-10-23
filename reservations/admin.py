from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Custom admin interface for Reservation model."""

    list_display = [
        'id',
        'reservation_code',
        'passenger_name',
        'passenger_email',
        'get_flight_info',
        'status',
        'created_at',
    ]

    list_filter = ['status', 'created_at', 'flight__departure', 'flight__destination']
    search_fields = ['reservation_code', 'passenger_name', 'passenger_email', 'flight__flight_number']
    ordering = ['-created_at']
    readonly_fields = ['id', 'reservation_code', 'created_at']

    fieldsets = (
        ('Passenger Information', {
            'fields': ('passenger_name', 'passenger_email')
        }),
        ('Booking Details', {
            'fields': ('flight', 'reservation_code', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    actions = ['cancel_reservations']

    def get_flight_info(self, obj):
        """Return flight number and route."""
        return f"{obj.flight.flight_number}: {obj.flight.departure} → {obj.flight.destination}"
    get_flight_info.short_description = 'Flight'

    def cancel_reservations(self, request, queryset):
        """Bulk action to cancel multiple reservations."""
        updated = queryset.filter(status=True).update(status=False)
        self.message_user(request, f"{updated} reservation(s) cancelled successfully.")
    cancel_reservations.short_description = "Cancel selected reservations"
