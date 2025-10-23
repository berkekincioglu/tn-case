from django.contrib import admin
from .models import Airplane


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    """Custom admin interface for Airplane model."""

    list_display = ['id','tail_number', 'model', 'capacity', 'production_year', 'status', 'get_flight_count']
    list_filter = ['status', 'production_year']
    search_fields = ['tail_number', 'model']
    ordering = ['-production_year', 'tail_number']
    readonly_fields = ['id']

    def get_flight_count(self, obj):
        """Return number of flights for this airplane."""
        return obj.flights.count()

    get_flight_count.short_description = 'Total Flights'
