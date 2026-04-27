from datetime import date as date_cls

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

from rooms.models import Room


class Booking(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmee'),
        ('ANNULEE', 'Annulee'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')
    purpose = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'date', 'start_time'],
                name='unique_room_date_start_time',
            )
        ]
        indexes = [
            models.Index(fields=['room', 'date']),
            models.Index(fields=['user', 'date']),
        ]

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("L'heure de fin doit etre apres l'heure de debut.")

        if self.date and self.date < date_cls.today():
            raise ValidationError('La date de reservation ne peut pas etre dans le passe.')

        if not self.room_id or not self.date:
            return

        conflicts = Booking.objects.filter(
            room=self.room,
            date=self.date,
            status__in=['EN_ATTENTE', 'CONFIRMEE'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)

        if conflicts.exists():
            raise ValidationError('Conflit detecte : cette salle est deja reservee sur ce creneau.')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.room} - {self.date} {self.start_time}-{self.end_time}'
