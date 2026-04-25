from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, time, timedelta
from .models import Booking
from rooms.models import Room
from django.contrib.auth import get_user_model

User = get_user_model()


class BookingModelTest(TestCase):
    """Tests pour le modèle Booking."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.room = Room.objects.create(
            name='Salle Test',
            capacity=10
        )
        self.booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            date=date.today() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(10, 0),
            purpose='Réunion test'
        )
    
    def test_booking_creation(self):
        """Test la création d'une réservation."""
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.room, self.room)
        self.assertEqual(self.booking.status, 'EN_ATTENTE')
    
    def test_booking_str(self):
        """Test la représentation string d'une réservation."""
        expected = f"Salle Test - {self.booking.date} {self.booking.start_time}-{self.booking.end_time}"
        self.assertEqual(str(self.booking), expected)
    
    def test_invalid_time_range(self):
        """Test qu'une réservation avec heure invalide est rejetée."""
        from django.core.exceptions import ValidationError
        
        invalid_booking = Booking(
            user=self.user,
            room=self.room,
            date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(9, 0),  # Fin avant début
            purpose='Test'
        )
        
        with self.assertRaises(ValidationError):
            invalid_booking.save()


class BookingViewSetTest(TestCase):
    """Tests pour le BookingViewSet."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.room = Room.objects.create(
            name='Salle Test',
            capacity=10
        )
        self.tomorrow = date.today() + timedelta(days=1)
    
    def test_booking_create_authenticated(self):
        """Test la création d'une réservation par un utilisateur authentifié."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/bookings/', {
            'room': self.room.id,
            'date': str(self.tomorrow),
            'start_time': '09:00',
            'end_time': '10:00',
            'purpose': 'Réunion'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)
    
    def test_booking_create_unauthenticated(self):
        """Test que la création sans authentification est refusée."""
        response = self.client.post('/api/bookings/', {
            'room': self.room.id,
            'date': str(self.tomorrow),
            'start_time': '09:00',
            'end_time': '10:00',
            'purpose': 'Réunion'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_booking_conflict_detection(self):
        """Test la détection de conflits de réservation."""
        # Créer une réservation existante
        existing = Booking.objects.create(
            user=self.user,
            room=self.room,
            date=self.tomorrow,
            start_time=time(9, 0),
            end_time=time(10, 0),
            purpose='Réunion 1',
            status='CONFIRMEE'
        )
        
        # Essayer de créer une réservation en conflit
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post('/api/bookings/', {
            'room': self.room.id,
            'date': str(self.tomorrow),
            'start_time': '09:30',  # Chevauchement
            'end_time': '10:30',
            'purpose': 'Réunion 2'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Conflit', str(response.data))
    
    def test_booking_user_isolation(self):
        """Test que les utilisateurs voient seulement leurs propres réservations."""
        booking1 = Booking.objects.create(
            user=self.user,
            room=self.room,
            date=self.tomorrow,
            start_time=time(9, 0),
            end_time=time(10, 0),
            purpose='Réunion 1'
        )
        
        booking2 = Booking.objects.create(
            user=self.other_user,
            room=self.room,
            date=self.tomorrow,
            start_time=time(11, 0),
            end_time=time(12, 0),
            purpose='Réunion 2'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/bookings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['purpose'], 'Réunion 1')
    
    def test_booking_cancel(self):
        """Test l'annulation d'une réservation."""
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            date=self.tomorrow,
            start_time=time(9, 0),
            end_time=time(10, 0),
            purpose='Réunion'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'ANNULEE')

    def test_conflict(self):
        Booking.objects.create(
            user=self.user,
            room=self.room,
            date=date.today(),
            start_time=time(10,0),
            end_time=time(12,0)
        )

        booking2 = Booking(
            user=self.user,
            room=self.room,
            date=date.today(),
            start_time=time(11,0),
            end_time=time(13,0)
        )

        with self.assertRaises(Exception):
            booking2.full_clean()