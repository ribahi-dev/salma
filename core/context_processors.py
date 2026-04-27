import os


def branding(request):
    google_enabled = bool(os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'))
    return {
        'platform_name': 'EMSI Room Booking',
        'platform_short_name': 'EMSI Booking',
        'google_oauth_enabled': google_enabled,
    }
