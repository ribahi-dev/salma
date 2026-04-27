from datetime import datetime

from rest_framework import serializers

from rooms.models import Room
from users.serializers import CustomUserSerializer

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    room_details = serializers.SerializerMethodField(read_only=True)
    conflicts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'room',
            'room_details',
            'date',
            'start_time',
            'end_time',
            'status',
            'purpose',
            'conflicts',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'conflicts']

    def get_room_details(self, obj):
        return {
            'id': obj.room.id,
            'code': obj.room.code,
            'name': obj.room.display_name,
            'capacity': obj.room.capacity,
            'floor': obj.room.floor,
            'room_type': obj.room.room_type,
            'location': obj.room.location,
            'equipment': obj.room.equipment,
        }

    def get_conflicts(self, obj):
        conflicts = Booking.objects.filter(
            room=obj.room,
            date=obj.date,
            status__in=['EN_ATTENTE', 'CONFIRMEE'],
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time,
        ).exclude(pk=obj.pk).values('id', 'start_time', 'end_time', 'user__username')
        return list(conflicts)

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        booking_date = attrs.get('date')
        room = attrs.get('room')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("L'heure de fin doit etre apres l'heure de debut.")

        if booking_date and booking_date < datetime.now().date():
            raise serializers.ValidationError('La date ne peut pas etre dans le passe.')

        if room and not room.is_active:
            raise serializers.ValidationError('Cette salle est inactive et ne peut pas etre reservee.')

        if booking_date and room and start_time and end_time:
            conflicts = Booking.objects.filter(
                room=room,
                date=booking_date,
                status__in=['EN_ATTENTE', 'CONFIRMEE'],
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)

            if conflicts.exists():
                conflicting_bookings = [f"{b.start_time}-{b.end_time} ({b.user.username})" for b in conflicts]
                raise serializers.ValidationError(
                    f"Conflit detecte: la salle est reservee: {', '.join(conflicting_bookings)}"
                )

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BookingAvailabilitySerializer(serializers.Serializer):
    room = serializers.IntegerField()
    date = serializers.DateField()

    def validate(self, attrs):
        try:
            Room.objects.get(id=attrs['room'])
        except Room.DoesNotExist:
            raise serializers.ValidationError('Salle non trouvee.')
        return attrs
