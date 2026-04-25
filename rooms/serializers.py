from rest_framework import serializers
from .models import Room
from django.db.models import Count


class RoomSerializer(serializers.ModelSerializer):
    booking_count = serializers.SerializerMethodField()
    upcoming_bookings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'location', 'description', 'is_active', 'booking_count', 'upcoming_bookings_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'booking_count', 'upcoming_bookings_count', 'created_at', 'updated_at']
    
    def get_booking_count(self, obj):
        """Retourne le nombre total de réservations pour cette salle."""
        return obj.booking_set.count()
    
    def get_upcoming_bookings_count(self, obj):
        """Retourne le nombre de réservations à venir."""
        from datetime import datetime
        today = datetime.now().date()
        return obj.booking_set.filter(date__gte=today, status__in=['EN_ATTENTE', 'CONFIRMEE']).count()
