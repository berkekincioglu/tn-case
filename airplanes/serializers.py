from rest_framework import serializers
from .models import Airplane
from datetime import datetime


class AirplaneSerializer(serializers.ModelSerializer):
    """Serializer for Airplane model with validation and computed fields."""

    total_flights = serializers.SerializerMethodField()

    class Meta:
        model = Airplane
        fields = [
            'id',
            'tail_number',
            'model',
            'capacity',
            'production_year',
            'status',
            'total_flights',
        ]
        read_only_fields = ['id', 'total_flights']

    def get_total_flights(self, obj):
        """Return total number of flights for this airplane."""
        return obj.flights.count()

    def validate_capacity(self, value):
        """Validate capacity is within reasonable range."""
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1.")
        if value > 1000:
            raise serializers.ValidationError("Capacity seems unrealistic. Maximum allowed is 1000.")
        return value

    def validate_production_year(self, value):
        """Validate production year is not in future and not too old."""
        current_year = datetime.now().year

        if value > current_year:
            raise serializers.ValidationError(
                f"Production year cannot be in the future. Current year is {current_year}."
            )
        if value < 1950:
            raise serializers.ValidationError("Production year seems too old. Minimum allowed is 1950.")

        return value


class AirplaneListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing airplanes with essential fields only."""

    class Meta:
        model = Airplane
        fields = ['id', 'tail_number', 'model', 'capacity', 'status']
        read_only_fields = fields
