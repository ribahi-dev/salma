from rest_framework import permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from .models import Booking
from .serializers import BookingSerializer, BookingAvailabilitySerializer
from rooms.models import Room
from core.permissions import IsBookingOwnerOrStaff


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.order_by('date', 'start_time')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'date', 'room']
    search_fields = ['room__name', 'purpose', 'user__username']
    ordering_fields = ['date', 'start_time', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.order_by('-created_at')
        return Booking.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def check_availability(self, request):
        """Vérifier la disponibilité d'une salle pour une date donnée."""
        serializer = BookingAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        room_id = serializer.validated_data['room']
        date = serializer.validated_data['date']
        
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Salle non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Récupérer les réservations confirmées/en attente pour ce jour
        bookings = Booking.objects.filter(
            room=room,
            date=date,
            status__in=['EN_ATTENTE', 'CONFIRMEE']
        ).order_by('start_time').values('start_time', 'end_time', 'user__username', 'status')
        
        return Response({
            'room': {'id': room.id, 'name': room.name, 'capacity': room.capacity},
            'date': date,
            'bookings': list(bookings),
            'availability': self._calculate_availability(list(bookings))
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """Annuler une réservation."""
        booking = self.get_object()
        
        # Vérifier la permission
        if booking.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Vous n\'avez pas la permission d\'annuler cette réservation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status == 'ANNULEE':
            return Response(
                {'error': 'Cette réservation est déjà annulée.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'ANNULEE'
        booking.save()
        return Response({'message': 'Réservation annulée.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def confirm(self, request, pk=None):
        """Confirmer une réservation (admin seulement)."""
        booking = self.get_object()
        
        if booking.status == 'CONFIRMEE':
            return Response(
                {'error': 'Cette réservation est déjà confirmée.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CONFIRMEE'
        booking.save()
        return Response({'message': 'Réservation confirmée.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_bookings(self, request):
        """Récupérer les réservations de l'utilisateur actuel."""
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @staticmethod
    def _calculate_availability(bookings):
        """Calculer les créneaux disponibles."""
        # Créneaux de travail: 8h à 18h
        available_slots = []
        busy_times = [(b['start_time'], b['end_time']) for b in bookings]
        
        # Trier les heures occupées
        busy_times.sort()
        
        # Vérifier les gaps
        from datetime import time
        current_time = time(8, 0)
        end_of_day = time(18, 0)
        
        for start, end in busy_times:
            if current_time < start:
                available_slots.append({'start': str(current_time), 'end': str(start)})
            current_time = max(current_time, end)
        
        if current_time < end_of_day:
            available_slots.append({'start': str(current_time), 'end': str(end_of_day)})
        
        return available_slots
