from django.apps import AppConfig


class SqualaetpConfig(AppConfig):
    name = 'squalaetp'

    def ready(self):
        import squalaetp.signals
