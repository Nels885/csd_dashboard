from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from dashboard.models import Post, ShowCollapse, UserProfile, WebLink


class Command(BaseCommand):
    help = 'Clear Dashboard tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--post',
            action='store_true',
            dest='post',
            help='Clear Poq table',
        )
        parser.add_argument(
            '--showcollapse',
            action='store_true',
            dest='showcollapse',
            help='Clear Poq table',
        )
        parser.add_argument(
            '--userprofile',
            action='store_true',
            dest='userprofile',
            help='Clear Poq table',
        )
        parser.add_argument(
            '--weblink',
            action='store_true',
            dest='weblink',
            help='Clear Poq table',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='Clear Dashboard tables',
        )

    def handle(self, *args, **options):

        if options['post']:
            Post.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Post, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table Post terminée!"))

        if options['showcollapse']:
            ShowCollapse.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ShowCollapse, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table ShowCollapse terminée!"))

        if options['userprofile']:
            UserProfile.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [UserProfile, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table UserProfile terminée!"))

        if options['weblink']:
            WebLink.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [WebLink, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données de la table WebLink terminée!"))

        if options['all']:
            Post.objects.all().delete()
            ShowCollapse.objects.all().delete()
            UserProfile.objects.all().delete()
            WebLink.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Post, ShowCollapse, UserProfile, WebLink])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Suppression des données des tables de Dashboard terminée!"))
