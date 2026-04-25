from rest_framework import serializers
from datetime import datetime, timedelta
from .models import Booking
from rooms.models import Room
from users.serializers import CustomUserSerializer


class BookingSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    room_details = serializers.SerializerMethodField(read_only=True)
    conflicts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'room', 'room_details', 'date', 'start_time', 'end_time', 'status', 'purpose', 'conflicts', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'conflicts']

    def get_room_details(self, obj):
        """Retourne les détails complets de la salle."""
        return {
            'id': obj.room.id,
            'name': obj.room.name,
            'capacity': obj.room.capacity,
            'location': obj.room.location,
        }

    def get_conflicts(self, obj):
        """Retourne les réservations en conflit."""
        conflicts = Booking.objects.filter(
            room=obj.room,
            date=obj.date,
            status__in=['EN_ATTENTE', 'CONFIRMEE'],
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time
        ).exclude(pk=obj.pk).values('id', 'start_time', 'end_time', 'user__username')
        return list(conflicts)

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        date = attrs.get('date')
        room = attrs.get('room')

        # Validation basique des heures
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("L'heure de fin doit être après l'heure de début.")

        # Validation date pas dans le passé
        if date and date < datetime.now().date():
            raise serializers.ValidationError("La date ne peut pas être dans le passé.")

        # Détection de conflits
        if date and room and start_time and end_time:
            conflicts = Booking.objects.filter(
                room=room,
                date=date,
                status__in=['EN_ATTENTE', 'CONFIRMEE'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            # Exclure la réservation actuelle si c'est une modification
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)

            if conflicts.exists():
                conflicting_bookings = [
                    f"{b.start_time}-{b.end_time} ({b.user.username})"
                    for b in conflicts
                ]
                raise serializers.ValidationError(
                    f"Conflit détecté: la salle est réservée: {', '.join(conflicting_bookings)}"
                )

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BookingAvailabilitySerializer(serializers.Serializer):
    """Serializer pour vérifier les créneaux disponibles."""
    room = serializers.IntegerField()
    date = serializers.DateField()
    
    def validate(self, attrs):
        try:
            Room.objects.get(id=attrs['room'])
        except Room.DoesNotExist:
            raise serializers.ValidationError("Salle non trouvée.")
        return attrs
