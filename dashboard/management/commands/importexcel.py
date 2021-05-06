import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the all tables in the database'

    def handle(self, *args, **options):
        self.stdout.write("[IMPORT_EXCEL] Waiting...")

        call_command("loadraspeedi")
        call_command("programing")
        # call_command("corvet")
        call_command("loadsqualaetp", "--xelon_update")
        call_command("importcorvet", "--squalaetp")
        call_command("exportsqualaetp")
        call_command("loadsqualaetp", "--relations")

        self.stdout.write(self.style.SUCCESS("[IMPORT_EXCEL] Update completed."))
