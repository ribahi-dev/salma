from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'emsi_id',
            'role',
            'department',
            'phone',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-select' if name == 'role' else 'form-control'
            field.widget.attrs.setdefault('class', css)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Cet email est deja utilise.')
        return email

    def clean_emsi_id(self):
        emsi_id = self.cleaned_data.get('emsi_id', '').strip().upper()
        if emsi_id and User.objects.filter(emsi_id__iexact=emsi_id).exists():
            raise forms.ValidationError('Cet identifiant EMSI est deja utilise.')
        return emsi_id


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'emsi_id', 'phone', 'department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        query = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if email and query.exists():
            raise forms.ValidationError('Cet email est deja utilise.')
        return email

    def clean_emsi_id(self):
        emsi_id = self.cleaned_data.get('emsi_id', '').strip().upper()
        query = User.objects.filter(emsi_id__iexact=emsi_id).exclude(pk=self.instance.pk)
        if emsi_id and query.exists():
            raise forms.ValidationError('Cet identifiant EMSI est deja utilise.')
        return emsi_id
