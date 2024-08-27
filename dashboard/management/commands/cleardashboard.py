from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from dashboard.models import Post, ShowCollapse, UserProfile, WebLink, Contract


class Command(BaseCommand):
    help = 'Clear Dashboard tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--post',
            action='store_true',
            dest='post',
            help='Clear Post table',
        )
        parser.add_argument(
            '--showcollapse',
            action='store_true',
            dest='showcollapse',
            help='Clear ShowCollapse table',
        )
        parser.add_argument(
            '--userprofile',
            action='store_true',
            dest='userprofile',
            help='Clear UserProfile table',
        )
        parser.add_argument(
            '--weblink',
            action='store_true',
            dest='weblink',
            help='Clear WebLink table',
        )
        parser.add_argument(
            '--contract',
            action='store_true',
            dest='contract',
            help='Clear Contract table',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='Clear Dashboard tables',
        )

    def handle(self, *args, **options):
        message = "Deleting data from table {0} completed !"
        if options['post']:
            Post.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Post, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS(message.format('Post')))

        if options['showcollapse']:
            ShowCollapse.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [ShowCollapse, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS(message.format('ShowCollapse')))

        if options['userprofile']:
            UserProfile.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [UserProfile, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS(message.format('UserProfile')))

        if options['weblink']:
            WebLink.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [WebLink, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS(message.format('WebLink')))

        if options['contract']:
            Contract.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Contract, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS(message.format('Contract')))

        if options['all']:
            Post.objects.all().delete()
            ShowCollapse.objects.all().delete()
            UserProfile.objects.all().delete()
            WebLink.objects.all().delete()
            Contract.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(
                no_style(), [Post, ShowCollapse, UserProfile, WebLink, Contract])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Deleting data from Dashboard tables completed !"))
