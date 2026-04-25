"""
Script d'initialisation de la base de données avec des données de test.
Lancez avec: python manage.py shell < initialize_db.py
"""

from django.contrib.auth import get_user_model
from rooms.models import Room
from bookings.models import Booking
from sris.models import AppSetting
from datetime import date, time, timedelta

User = get_user_model()

# Créer un utilisateur admin
admin_user = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_staff': True,
        'is_superuser': True,
        'first_name': 'Admin',
        'last_name': 'User',
        'department': 'Management'
    }
)[0]

if not admin_user.has_usable_password():
    admin_user.set_password('admin123')
    admin_user.save()

print(f"✓ Admin créé: {admin_user.username}")

# Créer des utilisateurs de test
test_users = [
    {
        'username': 'alice',
        'email': 'alice@example.com',
        'first_name': 'Alice',
        'last_name': 'Johnson',
        'department': 'IT',
        'phone': '0612345678'
    },
    {
        'username': 'bob',
        'email': 'bob@example.com',
        'first_name': 'Bob',
        'last_name': 'Smith',
        'department': 'HR',
        'phone': '0623456789'
    },
    {
        'username': 'charlie',
        'email': 'charlie@example.com',
        'first_name': 'Charlie',
        'last_name': 'Brown',
        'department': 'Finance',
        'phone': '0634567890'
    }
]

for user_data in test_users:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults=user_data
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"✓ Utilisateur créé: {user.username}")

# Créer des salles
rooms_data = [
    {
        'name': 'Salle de Conférence A',
        'capacity': 20,
        'location': 'Bâtiment 1, Étage 1',
        'description': 'Grande salle de conférence avec vidéoprojecteur et tableau blanc'
    },
    {
        'name': 'Salle de Réunion B',
        'capacity': 10,
        'location': 'Bâtiment 1, Étage 2',
        'description': 'Salle de réunion intime'
    },
    {
        'name': 'Amphithéâtre C',
        'capacity': 50,
        'location': 'Bâtiment 2, Rez-de-chaussée',
        'description': 'Grand amphithéâtre pour présentations'
    },
    {
        'name': 'Salle de Formation D',
        'capacity': 30,
        'location': 'Bâtiment 2, Étage 1',
        'description': 'Salle avec postes informatiques'
    },
    {
        'name': 'Bureau Directeur E',
        'capacity': 5,
        'location': 'Bâtiment 1, Étage 3',
        'description': 'Bureau équipé pour réunions'
    },
]

for room_data in rooms_data:
    room, created = Room.objects.get_or_create(
        name=room_data['name'],
        defaults=room_data
    )
    if created:
        print(f"✓ Salle créée: {room.name}")

# Créer quelques réservations de test
tomorrow = date.today() + timedelta(days=1)
alice = User.objects.get(username='alice')
bob = User.objects.get(username='bob')
salle_a = Room.objects.get(name='Salle de Conférence A')
salle_b = Room.objects.get(name='Salle de Réunion B')

bookings_data = [
    {
        'user': alice,
        'room': salle_a,
        'date': tomorrow,
        'start_time': time(9, 0),
        'end_time': time(10, 0),
        'purpose': 'Réunion d\'équipe',
        'status': 'CONFIRMEE'
    },
    {
        'user': bob,
        'room': salle_b,
        'date': tomorrow,
        'start_time': time(14, 0),
        'end_time': time(15, 30),
        'purpose': 'Entretien d\'embauche',
        'status': 'EN_ATTENTE'
    },
]

for booking_data in bookings_data:
    booking, created = Booking.objects.get_or_create(
        user=booking_data['user'],
        room=booking_data['room'],
        date=booking_data['date'],
        start_time=booking_data['start_time'],
        defaults={k: v for k, v in booking_data.items() if k not in ['user', 'room', 'date', 'start_time']}
    )
    if created:
        print(f"✓ Réservation créée: {booking.room} pour {booking.user}")

# Créer des settings
settings_data = [
    {
        'key': 'MAX_BOOKING_DAYS',
        'label': 'Nombre max de jours pour réserver',
        'value': '30',
        'description': 'Nombre maximum de jours à l\'avance qu\'un utilisateur peut réserver'
    },
    {
        'key': 'MIN_BOOKING_DURATION',
        'label': 'Durée minimale d\'une réservation',
        'value': '30',
        'description': 'Durée minimale d\'une réservation en minutes'
    },
    {
        'key': 'MAX_BOOKING_DURATION',
        'label': 'Durée maximale d\'une réservation',
        'value': '480',
        'description': 'Durée maximale d\'une réservation en minutes'
    },
]

for setting_data in settings_data:
    setting, created = AppSetting.objects.get_or_create(
        key=setting_data['key'],
        defaults=setting_data
    )
    if created:
        print(f"✓ Setting créé: {setting.key}")

print("\n✓ Base de données initialisée avec succès!")
print("\nComptes de test:")
print("- Admin: admin / admin123")
print("- Alice: alice / password123")
print("- Bob: bob / password123")
print("- Charlie: charlie / password123")
