from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'emsi_id',
            'phone',
            'department',
            'role',
        ]


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'emsi_id',
            'phone',
            'department',
            'role',
        ]

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Cet email est deja utilise.')
        return value.lower()

    def validate_emsi_id(self, value):
        if value and CustomUser.objects.filter(emsi_id__iexact=value).exists():
            raise serializers.ValidationError('Cet identifiant EMSI est deja utilise.')
        return value.upper() if value else value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
