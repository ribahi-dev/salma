from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField('Téléphone', max_length=30, blank=True)
    department = models.CharField('Département', max_length=255, blank=True)

    def __str__(self):
        return self.username
