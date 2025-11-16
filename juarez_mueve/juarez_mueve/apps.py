from django.apps import AppConfig

class JuarezMueveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'juarez_mueve'


    def ready(self):
        import juarez_mueve.signals 
