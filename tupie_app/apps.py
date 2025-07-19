from django.apps import AppConfig

class TupieAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tupie_app'

    def ready(self):
        import tupie_app.signals
