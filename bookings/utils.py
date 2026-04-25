"""Utilitaires pour l'application de réservation de salles."""

from datetime import datetime, timedelta, time as datetime_time
from .models import Booking
from rooms.models import Room


def get_room_availability(room_id, date):
    """
    Récupère les créneaux disponibles pour une salle à une date donnée.
    
    Args:
        room_id (int): ID de la salle
        date (date): Date pour laquelle vérifier la disponibilité
    
    Returns:
        dict: Informations de disponibilité avec les créneaux libres
    """
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return None
    
    # Récupérer les réservations confirmées et en attente
    bookings = Booking.objects.filter(
        room=room,
        date=date,
        status__in=['EN_ATTENTE', 'CONFIRMEE']
    ).order_by('start_time').values_list('start_time', 'end_time')
    
    # Calculer les créneaux disponibles
    available_slots = calculate_available_slots(list(bookings))
    
    return {
        'room': {
            'id': room.id,
            'name': room.name,
            'capacity': room.capacity,
            'location': room.location,
        },
        'date': date,
        'bookings_count': len(bookings),
        'available_slots': available_slots,
    }


def calculate_available_slots(busy_times):
    """
    Calcule les créneaux disponibles basé sur les heures occupées.
    
    Args:
        busy_times (list): Liste de tuples (start_time, end_time)
    
    Returns:
        list: Créneaux disponibles
    """
    # Heures de travail: 8h à 18h
    work_start = datetime_time(8, 0)
    work_end = datetime_time(18, 0)
    
    if not busy_times:
        return [{'start': str(work_start), 'end': str(work_end)}]
    
    available_slots = []
    busy_times = sorted(busy_times)
    
    current_time = work_start
    
    for start, end in busy_times:
        if current_time < start:
            available_slots.append({
                'start': str(current_time),
                'end': str(start)
            })
        current_time = max(current_time, end)
    
    if current_time < work_end:
        available_slots.append({
            'start': str(current_time),
            'end': str(work_end)
        })
    
    return available_slots


def check_booking_conflict(room, date, start_time, end_time, exclude_id=None):
    """
    Vérifie s'il existe un conflit de réservation.
    
    Args:
        room (Room): Salle à vérifier
        date (date): Date de la réservation
        start_time (time): Heure de début
        end_time (time): Heure de fin
        exclude_id (int): ID de réservation à exclure (pour les modifications)
    
    Returns:
        list: Liste des réservations en conflit
    """
    conflicts = Booking.objects.filter(
        room=room,
        date=date,
        status__in=['EN_ATTENTE', 'CONFIRMEE'],
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    
    if exclude_id:
        conflicts = conflicts.exclude(pk=exclude_id)
    
    return list(conflicts)


def get_user_bookings_summary(user):
    """
    Retourne un résumé des réservations d'un utilisateur.
    
    Args:
        user: Utilisateur
    
    Returns:
        dict: Statistiques des réservations
    """
    today = datetime.now().date()
    
    all_bookings = Booking.objects.filter(user=user)
    upcoming = all_bookings.filter(date__gte=today).order_by('date')
    past = all_bookings.filter(date__lt=today)
    
    return {
        'total_bookings': all_bookings.count(),
        'upcoming_bookings': upcoming.count(),
        'past_bookings': past.count(),
        'cancelled_bookings': all_bookings.filter(status='ANNULEE').count(),
        'confirmed_bookings': all_bookings.filter(status='CONFIRMEE').count(),
    }
