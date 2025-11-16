from django.shortcuts import redirect
from django.contrib import messages

def rol_requerido(*roles):
    def decorator(view_function):
        def wrapper(request, *args, **kwargs):
            profile = request.user.profile

            if profile.rol not in roles:
                messages.error(request, "No tienes permiso para acceder a esta sección.")
                return redirect('index')

            return view_function(request, *args, **kwargs)
        return wrapper
    return decorator
