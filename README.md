# EMSI Booking - Plateforme de reservation des salles

Application Django de reservation et de pilotage des salles EMSI, pensee pour un usage reel:
- inscription de nouveaux utilisateurs
- connexion par email ou Google
- soumission de demandes de reservation
- approbation par un admin central
- suivi des salles, des etages et des decisions

## Fonctionnalites

- comptes utilisateurs reels: etudiant, enseignant, professeur
- email unique et profil EMSI complet
- connexion web, API REST et JWT
- connexion Google OAuth
- creation, modification et annulation de reservations
- workflow admin: en attente, approuvee, refusee, annulee
- centre d'administration avec filtres et actions groupees
- notifications email sur creation et traitement des demandes
- calendrier de reservations et supervision par etage
- regles metier reelles:
  - prevention des conflits
  - capacite maximale des salles
  - duree minimale et maximale
  - fenetre de reservation configurable
  - horaires de reservation configurables

## Stack

- Django 5.2
- Django REST Framework
- django-allauth
- SimpleJWT
- WhiteNoise
- Bootstrap 5
- FullCalendar

## Installation locale

```bash
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Acces local

- web: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- admin Django: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- API: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

## Comptes de demonstration

- `admin / admin123`
- `fatine / password123`
- `salma / password123`
- `youssef / password123`

## Commandes utiles

```bash
python manage.py check
python manage.py test bookings rooms users
python manage.py seed_demo
python manage.py createsuperuser
python manage.py collectstatic
```

## Configuration production

### 1. Variables d'environnement

Copier `.env.example` puis renseigner:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `EMAIL_*`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### 2. Base de donnees

Par defaut le projet utilise SQLite.

Pour la production, utiliser PostgreSQL via:

```env
DATABASE_URL=postgresql://user:password@host:5432/emsi_booking
```

### 3. Emails reels

Configurer un SMTP reel pour:
- l'accueil des nouveaux utilisateurs
- les notifications de nouvelles demandes
- les validations/refus/annulations admin

Exemple:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@votre-domaine.ma
```

### 4. Fichiers statiques

Le projet est prepare pour WhiteNoise:

```bash
python manage.py collectstatic --noinput
```

### 5. Lancement serveur

Exemple Linux:

```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

## Regles metier configurables

Les regles suivantes sont stockees dans `AppSetting`:
- `MAX_BOOKING_DAYS`
- `MIN_BOOKING_DURATION`
- `MAX_BOOKING_DURATION`
- `WORKDAY_START_HOUR`
- `WORKDAY_END_HOUR`

## Qualite

- validations serveur sur formulaires, serializers et modeles
- tests backend automatisees
- smoke test locale du parcours utilisateur et admin

## Statut

Base solide pour deployment reel EMSI, avec onboarding utilisateur, administration centrale et reservation exploitable en production.
