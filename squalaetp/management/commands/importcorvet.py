from django.core.management.base import BaseCommand
from constance import config

from utils.scraping import ScrapingCorvet


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('vin', type=str)

    def handle(self, *args, **options):
        if options['vin']:
            vin = options['vin']
            data = ScrapingCorvet(config.CORVET_USER, config.CORVET_PWD).result(vin)
            self.stdout.write(data)
