from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


def build_username(email, first_name='', last_name=''):
    if email and '@' in email:
        return email.split('@', 1)[0][:150]
    raw = f'{first_name}{last_name}'.strip().lower().replace(' ', '')
    return (raw or 'emsi_user')[:150]


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        if not user.username:
            user.username = build_username(email=email, first_name=first_name, last_name=last_name)
        if not user.email:
            user.email = email
        if not user.first_name:
            user.first_name = first_name
        if not user.last_name:
            user.last_name = last_name
        return user
