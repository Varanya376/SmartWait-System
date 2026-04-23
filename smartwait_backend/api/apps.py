from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from .seed_data import seed_restaurants

        def seed(sender, **kwargs):
            seed_restaurants()

        post_migrate.connect(seed, sender=self)