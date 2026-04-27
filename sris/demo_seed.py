from datetime import date, time, timedelta

from django.contrib.auth import get_user_model

from bookings.models import Booking
from rooms.models import Room
from sris.models import AppSetting


User = get_user_model()


def ensure_user(username, password, **defaults):
    user, created = User.objects.get_or_create(username=username, defaults=defaults)
    if created or not user.has_usable_password():
        user.set_password(password)
    for field, value in defaults.items():
        setattr(user, field, value)
    user.save()
    return user


def build_room_payloads():
    payloads = []

    for floor in range(1, 7):
        for index in range(1, 9):
            code = f'SC{floor}{index:02d}'
            payloads.append(
                {
                    'building': 'EMSI',
                    'floor': floor,
                    'code': code,
                    'name': f'Salle de cours {code}',
                    'room_type': Room.TYPE_CLASSROOM,
                    'capacity': 32,
                    'location': f'EMSI - Etage {floor}',
                    'description': f'Salle de cours standard situee a l etage {floor}.',
                    'equipment': 'projecteur, tableau, wifi',
                    'is_active': True,
                }
            )

        for index in range(1, 3):
            code = f'LI{floor}{index:02d}'
            payloads.append(
                {
                    'building': 'EMSI',
                    'floor': floor,
                    'code': code,
                    'name': f'Laboratoire informatique {code}',
                    'room_type': Room.TYPE_LAB,
                    'capacity': 24,
                    'location': f'EMSI - Etage {floor}',
                    'description': f'Salle equipee en postes informatiques pour les TP a l etage {floor}.',
                    'equipment': 'ordinateurs, projecteur, climatisation, wifi',
                    'is_active': True,
                }
            )

    for index in range(1, 5):
        code = f'CONF{index:02d}'
        payloads.append(
            {
                'building': 'EMSI',
                'floor': 0,
                'code': code,
                'name': f'Salle de conference {index}',
                'room_type': Room.TYPE_CONFERENCE,
                'capacity': 120,
                'location': 'EMSI - Pole conferences',
                'description': 'Grande salle dediee aux conferences, soutenances et evenements.',
                'equipment': 'micro, sonorisation, projecteur, wifi, scene',
                'is_active': True,
            }
        )

    return payloads


def seed_demo_data():
    Room.objects.filter(code__isnull=True).delete()

    ensure_user(
        'admin',
        'admin123',
        email='admin@emsi.ma',
        first_name='Admin',
        last_name='EMSI',
        role=User.ROLE_PROFESSOR,
        emsi_id='EMSI-ADMIN',
        department='Administration',
        is_staff=True,
        is_superuser=True,
    )

    professor = ensure_user(
        'fatine',
        'password123',
        email='fatine@emsi-edu.ma',
        first_name='Fatine',
        last_name='Elbari',
        role=User.ROLE_PROFESSOR,
        emsi_id='EMSI-PROF-001',
        department='Informatique',
        phone='0611111111',
    )

    teacher = ensure_user(
        'salma',
        'password123',
        email='salma@emsi-edu.ma',
        first_name='Salma',
        last_name='Karim',
        role=User.ROLE_TEACHER,
        emsi_id='EMSI-ENS-014',
        department='Genie logiciel',
        phone='0622222222',
    )

    student = ensure_user(
        'youssef',
        'password123',
        email='youssef@emsi-edu.ma',
        first_name='Youssef',
        last_name='Alaoui',
        role=User.ROLE_STUDENT,
        emsi_id='EMSI-ELV-108',
        department='Reseaux',
        phone='0633333333',
    )

    created_rooms = {}
    for payload in build_room_payloads():
        room, _ = Room.objects.update_or_create(code=payload['code'], defaults=payload)
        created_rooms[room.code] = room

    tomorrow = date.today() + timedelta(days=1)
    next_week = date.today() + timedelta(days=7)

    bookings_data = [
        {
            'user': professor,
            'room': created_rooms['SC201'],
            'date': tomorrow,
            'start_time': time(9, 0),
            'end_time': time(11, 0),
            'purpose': 'Cours de genie logiciel',
            'status': 'CONFIRMEE',
        },
        {
            'user': teacher,
            'room': created_rooms['LI302'],
            'date': tomorrow,
            'start_time': time(14, 0),
            'end_time': time(16, 0),
            'purpose': 'TP developpement web',
            'status': 'EN_ATTENTE',
        },
        {
            'user': student,
            'room': created_rooms['CONF01'],
            'date': next_week,
            'start_time': time(10, 0),
            'end_time': time(12, 0),
            'purpose': 'Evenement club etudiants',
            'status': 'EN_ATTENTE',
        },
    ]

    for payload in bookings_data:
        Booking.objects.update_or_create(
            user=payload['user'],
            room=payload['room'],
            date=payload['date'],
            start_time=payload['start_time'],
            defaults={
                'end_time': payload['end_time'],
                'purpose': payload['purpose'],
                'status': payload['status'],
            },
        )

    settings_data = [
        (
            'MAX_BOOKING_DAYS',
            'Reservation maximum en avance',
            '45',
            "Nombre maximum de jours a l'avance pour reserver.",
        ),
        (
            'MIN_BOOKING_DURATION',
            'Duree minimale',
            '30',
            'Duree minimale d une reservation en minutes.',
        ),
        (
            'MAX_BOOKING_DURATION',
            'Duree maximale',
            '240',
            'Duree maximale d une reservation en minutes.',
        ),
    ]

    for key, label, value, description in settings_data:
        AppSetting.objects.update_or_create(
            key=key,
            defaults={'label': label, 'value': value, 'description': description, 'is_active': True},
        )

    return {
        'accounts': [
            'admin / admin123',
            'fatine / password123',
            'salma / password123',
            'youssef / password123',
        ],
        'rooms_count': len(created_rooms),
    }
