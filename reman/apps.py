from django.apps import AppConfig


class RemanConfig(AppConfig):
    name = 'reman'

    def ready(self):
        import reman.signals
