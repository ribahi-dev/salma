from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError
from rooms.models import Room

class Booking(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmée'),
        ('ANNULEE', 'Annulée'),
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

    def clean(self):
        # Vérification logique simple
        if self.start_time >= self.end_time:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")

        # 🔥 Détection de conflit (comme dans ton PDF)
        conflicts = Booking.objects.filter(
            room=self.room,
            date=self.date,
            status__in=['EN_ATTENTE', 'CONFIRMEE'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)

        if conflicts.exists():
            raise ValidationError("Conflit détecté : cette salle est déjà réservée sur ce créneau.")

    def save(self, *args, **kwargs):
        # 🔥 Transaction atomique (important pour éviter double réservation)
        with transaction.atomic():
            self.clean()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room} - {self.date} {self.start_time}-{self.end_time}"