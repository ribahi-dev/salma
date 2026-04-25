from rest_framework import permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from .models import Room
from .serializers import RoomSerializer
from core.permissions import IsStaffOrReadOnly
from bookings.utils import get_room_availability


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(is_active=True).order_by('name')
    serializer_class = RoomSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'capacity']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['name', 'capacity', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def availability(self, request, pk=None):
        """Vérifier la disponibilité d'une salle pour une date donnée."""
        room = self.get_object()
        date_str = request.query_params.get('date', datetime.now().date().isoformat())
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        availability = get_room_availability(room.id, date)
        return Response(availability)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def all_availability(self, request):
        """Vérifier la disponibilité de toutes les salles pour une date donnée."""
        date_str = request.query_params.get('date', datetime.now().date().isoformat())
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rooms = self.get_queryset()
        availability_data = []
        
        for room in rooms:
            availability = get_room_availability(room.id, date)
            if availability:
                availability_data.append(availability)
        
        return Response({
            'date': date,
            'rooms': availability_data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """Désactiver une salle."""
        room = self.get_object()
        room.is_active = False
        room.save()
        return Response({'message': f'Salle {room.name} désactivée.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """Activer une salle."""
        room = self.get_object()
        room.is_active = True
        room.save()
        return Response({'message': f'Salle {room.name} activée.'}, status=status.HTTP_200_OK)
