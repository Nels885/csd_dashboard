from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Auth data update'

    def add_arguments(self, parser):
        parser.add_argument(
            '-E',
            '--email_domain',
            dest='email_domain',
            help='Change email domain',
        )

    def handle(self, *args, **options):
        self.stdout.write("[AUTH] Waiting...")

        if options['email_domain'] is not None:
            users = User.objects.all()
            for user in users:
                if user.email:
                    old_domain = user.email.split("@")[-1]
                    user.email = user.email.replace(old_domain, options['email_domain'])
                    user.save()
            self.stdout.write(self.style.SUCCESS(f"[AUTH] Email domain update completed: USER = {users.count()}"))
