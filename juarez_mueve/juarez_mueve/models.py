from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    genero = models.CharField(
        max_length=20,
        choices=[
            ('Hombre', 'Hombre'),
            ('Mujer', 'Mujer'),
            ('Otro', 'Otro'),
            ('Prefiero no decir', 'Prefiero no decir'),
        ],
        blank=True,
        null=True
    )
    colonia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.first_name or self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)