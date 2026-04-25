# 🚀 QUICK START - 5 minutes pour lancer l'API

## Installation

```bash
cd "c:\Users\PCARABI\OneDrive\Desktop\projet pfa"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Résultats

- API disponible à: **http://localhost:8000/api/**
- Admin panel à: **http://localhost:8000/admin/**

## Tester l'API

### 1️⃣ Enregistrement
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user@test.com","password":"pass123"}'
```

### 2️⃣ Connexion
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}'
```
→ Copier le `access` token

### 3️⃣ Voir les salles
```bash
curl http://localhost:8000/api/rooms/
```

### 4️⃣ Créer une réservation
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer [VOTRE_TOKEN]" \
  -H "Content-Type: application/json" \
  -d '{
    "room":1,
    "date":"2024-04-25",
    "start_time":"14:00",
    "end_time":"15:00",
    "purpose":"Réunion"
  }'
```

## Données de test

Charger les données d'exemple:
```bash
python manage.py shell < initialize_db.py
```

Comptes créés:
- Admin: `admin` / `admin123`
- Alice: `alice` / `password123`
- Bob: `bob` / `password123`

## Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/register/` | POST | S'enregistrer |
| `/api/auth/token/` | POST | Se connecter |
| `/api/rooms/` | GET | Lister les salles |
| `/api/bookings/` | GET/POST | Mes réservations |
| `/api/settings/dashboard/` | GET | Statistiques |

## Lancer les tests

```bash
python manage.py test
```

---

**Pour plus de détails:** Voir [README.md](README.md) ou [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
