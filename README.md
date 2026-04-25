# Plateforme de Réservation de Salles - Backend Django

Une API REST complète pour la gestion des réservations de salles avec authentification JWT, gestion des utilisateurs et détection intelligente des conflits.

## 📋 Fonctionnalités

✅ **Authentification JWT** - Sécurité avec tokens JWT
✅ **Gestion des utilisateurs** - Création, modification, profils détaillés
✅ **Gestion des salles** - Création, recherche, disponibilité en temps réel
✅ **Système de réservation avancé** - Détection automatique des conflits, validation complète
✅ **Permissions granulaires** - Admin, Staff, Utilisateurs avec droits différenciés
✅ **Filtrage et recherche** - Filtrage avancé, pagination, recherche full-text
✅ **Statistiques** - Dashboard avec métriques en temps réel
✅ **Tests complets** - Suite de tests pour tous les modèles et endpoints
✅ **Documentation API** - Documentation Swagger/OpenAPI complète

## 🚀 Démarrage rapide

### Prérequis

- Python 3.10+
- pip ou pipenv

### Installation

1. **Cloner le projet**
```bash
cd "c:\Users\PCARABI\OneDrive\Desktop\projet pfa"
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Créer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

5. **Initialiser les données de test (optionnel)**
```bash
python manage.py shell < initialize_db.py
```

6. **Lancer le serveur**
```bash
python manage.py runserver
```

L'API sera disponible à `http://localhost:8000/api/`

## 📚 Documentation API

Voir [API_DOCUMENTATION.md](API_DOCUMENTATION.md) pour la documentation complète de tous les endpoints.

### Endpoints principaux

#### Authentication
- `POST /api/auth/token/` - Obtenir un token JWT
- `POST /api/auth/register/` - Créer un compte
- `GET /api/auth/me/` - Profil de l'utilisateur actuel

#### Utilisateurs
- `GET /api/users/` - Lister les utilisateurs
- `GET /api/users/{id}/` - Détails d'un utilisateur
- `GET /api/users/{id}/bookings/` - Réservations d'un utilisateur

#### Salles
- `GET /api/rooms/` - Lister les salles
- `POST /api/rooms/` - Créer une salle (staff)
- `GET /api/rooms/{id}/availability/?date=YYYY-MM-DD` - Vérifier la disponibilité
- `GET /api/rooms/all_availability/?date=YYYY-MM-DD` - Disponibilité de toutes les salles

#### Réservations
- `GET /api/bookings/` - Lister les réservations de l'utilisateur
- `POST /api/bookings/` - Créer une réservation
- `POST /api/bookings/{id}/cancel/` - Annuler une réservation
- `POST /api/bookings/check_availability/` - Vérifier les créneaux libres

#### Paramètres
- `GET /api/settings/` - Lister les paramètres
- `GET /api/settings/dashboard/` - Tableau de bord avec statistiques
- `GET /api/settings/system_health/` - État du système

## 🧪 Tests

### Lancer tous les tests
```bash
python manage.py test
```

### Lancer les tests d'une application spécifique
```bash
python manage.py test users.tests
python manage.py test rooms.tests
python manage.py test bookings.tests
python manage.py test sris.tests
```

### Avec couverture de code (optionnel)
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🏗️ Structure du projet

```
projet pfa/
├── core/                  # Configuration Django
│   ├── settings.py       # Configuration principale
│   ├── urls.py          # URLs principales
│   ├── permissions.py   # Permissions personnalisées
│   └── wsgi.py
├── users/               # Gestion des utilisateurs
│   ├── models.py        # CustomUser
│   ├── views.py         # UserViewSet
│   ├── serializers.py   # Sérializers
│   ├── tests.py         # Tests
│   └── admin.py         # Admin Django
├── rooms/               # Gestion des salles
│   ├── models.py        # Room
│   ├── views.py         # RoomViewSet
│   ├── serializers.py   # Sérializers
│   ├── tests.py         # Tests
│   └── admin.py         # Admin Django
├── bookings/            # Gestion des réservations
│   ├── models.py        # Booking avec validation
│   ├── views.py         # BookingViewSet
│   ├── serializers.py   # Sérializers
│   ├── utils.py         # Fonctions utilitaires
│   ├── tests.py         # Tests
│   ├── forms.py         # Formulaires Django
│   └── admin.py         # Admin Django
├── sris/                # Paramètres et statistiques
│   ├── models.py        # AppSetting
│   ├── views.py         # AppSettingViewSet
│   ├── serializers.py   # Sérializers
│   ├── tests.py         # Tests
│   └── admin.py         # Admin Django
├── db.sqlite3           # Base de données
├── manage.py            # Commandes Django
├── requirements.txt     # Dépendances
├── initialize_db.py     # Script d'initialisation
├── API_DOCUMENTATION.md # Documentation complète
└── README.md            # Ce fichier
```

## 🔐 Authentification

L'API utilise JWT pour l'authentification. 

### Flux d'authentification

1. **S'enregistrer**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

2. **Obtenir un token**
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword"
  }'
```

3. **Utiliser le token**
```bash
curl -X GET http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer <votre_token>"
```

## 📊 Système de réservation

### Validation automatique

Le système valide automatiquement:
- ✓ Les heures invalides (fin avant début)
- ✓ Les dates dans le passé
- ✓ Les conflits de réservation
- ✓ La capacité de la salle
- ✓ Les créneaux disponibles

### Détection de conflits

Avant d'accepter une réservation, le système:
1. Vérifie s'il existe une réservation chevauchante
2. Retourne les réservations en conflit avec les détails
3. Refuse la réservation si conflit détecté

### Exemple d'erreur de conflit
```json
{
  "non_field_errors": [
    "Conflit détecté: la salle est réservée: 09:30-10:30 (alice), 10:30-11:00 (bob)"
  ]
}
```

## 🔒 Permissions

### Anonyme
- Lecture seule sur les salles

### Utilisateur authentifié
- CRUD complet sur ses propres réservations
- Lecture sur les profils utilisateurs
- Lecture sur les salles et paramètres
- Création de réservations

### Staff
- Gestion complète des salles
- Gestion complète des réservations
- Confirmation des réservations
- Gestion des paramètres en lecture

### Admin
- Accès complet au système
- Gestion des utilisateurs
- Gestion des paramètres
- Accès à tous les endpoints

## 🎯 Cas d'usage courants

### Créer une réservation
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "room": 1,
    "date": "2024-04-25",
    "start_time": "14:00",
    "end_time": "15:00",
    "purpose": "Réunion d'\''équipe"
  }'
```

### Vérifier la disponibilité
```bash
curl -X POST http://localhost:8000/api/bookings/check_availability/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "room": 1,
    "date": "2024-04-25"
  }'
```

### Voir les statistiques
```bash
curl -X GET http://localhost:8000/api/settings/dashboard/ \
  -H "Authorization: Bearer <token>"
```

## 🐛 Dépannage

### Port déjà utilisé
```bash
python manage.py runserver 8001
```

### Migrations en conflit
```bash
python manage.py migrate --fake
python manage.py migrate
```

### Cache problématique
```bash
python manage.py clear_cache
```

### Erreur de base de données
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## 📈 Performance

### Pagination
Les listes sont paginées par défaut (20 résultats par page).
```bash
curl http://localhost:8000/api/bookings/?page=2
```

### Filtrage
Utilisez les paramètres de filtrage pour réduire les requêtes:
```bash
curl "http://localhost:8000/api/bookings/?status=CONFIRMEE&date=2024-04-25"
```

### Recherche
```bash
curl "http://localhost:8000/api/bookings/?search=reunion"
```

## 🚀 Déploiement

Pour la production:

1. **Définir DEBUG=False** dans settings.py
2. **Configurer ALLOWED_HOSTS**
3. **Utiliser une vraie base de données** (PostgreSQL recommandé)
4. **Configurer CORS** correctement
5. **Ajouter HTTPS**
6. **Utiliser gunicorn ou uWSGI**

```bash
# Exemple avec gunicorn
pip install gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

## 📝 Licence

Ce projet est fourni à titre éducatif.

## 👨‍💻 Support

Pour toute question ou problème, consultez la [documentation complète](API_DOCUMENTATION.md).

## 🎓 Technologies utilisées

- **Django 6.0.3** - Framework web
- **Django REST Framework** - API REST
- **SimpleJWT** - Authentification JWT
- **django-filter** - Filtrage
- **django-cors-headers** - CORS
- **SQLite** - Base de données (développement)

---

**Status**: ✅ Production-ready
**Dernière mise à jour**: 2024-04-21
**Version**: 1.0.0
