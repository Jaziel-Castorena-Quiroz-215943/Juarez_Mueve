from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Profile

@receiver(user_signed_up)
def fill_user_from_google(sender, request, user, **kwargs):
    """
    Completar nombre, apellidos y perfil al registrarse con Google.
    """

    # Google manda los datos en account.extra_data
    sociallogin = kwargs.get("sociallogin")
    extra = sociallogin.account.extra_data if sociallogin else {}

    # Extraer nombre y apellidos si existen
    first_name = extra.get("given_name") or ""
    last_name = extra.get("family_name") or ""

    # Guardar en User
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name

    user.save()

    # Crear o actualizar el perfil
    profile, created = Profile.objects.get_or_create(user=user)

    # Asignar rol seguro
    profile.rol = "CIUDADANO"

    profile.save()
