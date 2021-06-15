from django.apps import AppConfig


class PsaConfig(AppConfig):
    name = 'psa'

    def ready(self):
        import psa.signals
