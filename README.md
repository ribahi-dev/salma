# SRIS - Systeme de Reservation Intelligente des Salles

Application web Django pour la gestion des salles universitaires, des reservations et de la supervision administrative.

## Fonctionnalites

- inscription et connexion des utilisateurs
- gestion des roles: etudiant, enseignant, administrateur, administrateur systeme
- consultation et filtrage des salles
- creation, modification et annulation de reservations
- detection automatique des conflits horaires
- calendrier visuel des reservations
- tableau de bord avec indicateurs
- interface d'administration Django
- API REST avec JWT
- reinitialisation du mot de passe via le systeme Django

## Stack technique

- Python
- Django 5.2
- Django REST Framework
- SimpleJWT
- Bootstrap 5
- FullCalendar
- SQLite en developpement

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Acces

- web: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- api: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

## Comptes de demonstration

- `admin / admin123`
- `fatine / password123`
- `salma / password123`
- `youssef / password123`

## Commandes utiles

```bash
python manage.py check
python manage.py test
python manage.py seed_demo
python manage.py createsuperuser
```

## API principale

- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET /api/auth/me/`
- `GET /api/rooms/`
- `GET /api/bookings/`
- `POST /api/bookings/`
- `POST /api/bookings/check_availability/`
- `GET /api/settings/dashboard/`

## Qualite

- validations serveur sur les formulaires et serializers
- prevention des conflits de reservation
- contraintes et index en base
- tests automatises passes: `23/23`

## Production

Pour un deploiement production:

- passer sur PostgreSQL
- definir `DJANGO_DEBUG=False`
- configurer `DJANGO_ALLOWED_HOSTS`
- servir les fichiers statiques avec WhiteNoise ou un reverse proxy
- configurer un backend email reel

## Statut

Projet pret pour demonstration, soutenance et poursuite vers deploiement.
