from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Room
from django.contrib.auth import get_user_model

User = get_user_model()


class RoomModelTest(TestCase):
    """Tests pour le modèle Room."""
    
    def setUp(self):
        self.room = Room.objects.create(
            name='Salle A',
            capacity=10,
            location='Bâtiment 1',
            description='Grande salle de réunion'
        )
    
    def test_room_creation(self):
        """Test la création d'une salle."""
        self.assertEqual(self.room.name, 'Salle A')
        self.assertEqual(self.room.capacity, 10)
        self.assertEqual(self.room.is_active, True)
    
    def test_room_str(self):
        """Test la représentation string d'une salle."""
        self.assertEqual(str(self.room), 'Salle A')


class RoomViewSetTest(TestCase):
    """Tests pour le RoomViewSet."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.room = Room.objects.create(
            name='Salle B',
            capacity=15,
            location='Bâtiment 2'
        )
    
    def test_room_list(self):
        """Test la liste des salles (accessible sans authentification)."""
        response = self.client.get('/api/rooms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_room_detail(self):
        """Test les détails d'une salle."""
        response = self.client.get(f'/api/rooms/{self.room.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Salle B')
    
    def test_room_create_requires_staff(self):
        """Test que la création de salle require les droits staff."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/rooms/', {
            'name': 'Salle C',
            'capacity': 20,
            'location': 'Bâtiment 3'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
