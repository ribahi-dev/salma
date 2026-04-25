from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Tests pour le modèle CustomUser."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='123456789',
            department='IT'
        )
    
    def test_user_creation(self):
        """Test la création d'un utilisateur."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.phone, '123456789')
        self.assertEqual(self.user.department, 'IT')
    
    def test_user_str(self):
        """Test la représentation string d'un utilisateur."""
        self.assertEqual(str(self.user), 'testuser')


class UserViewSetTest(TestCase):
    """Tests pour le UserViewSet."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    def test_user_register(self):
        """Test l'enregistrement d'un nouvel utilisateur."""
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
    
    def test_current_user_view(self):
        """Test la récupération de l'utilisateur actuel."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_list_authenticated(self):
        """Test la liste des utilisateurs avec authentification."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
