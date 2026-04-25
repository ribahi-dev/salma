from django.http import JsonResponse

def home_view(request):
    return JsonResponse({
        "message": "Bienvenue sur l'API de gestion de réservations",
        "endpoints": {
            "admin": "/admin/",
            "auth": {
                "token": "/api/auth/token/",
                "refresh": "/api/auth/token/refresh/",
                "register": "/api/auth/register/",
                "me": "/api/auth/me/"
            },
            "api": "/api/"
        }
    })