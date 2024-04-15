from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Automatically make and apply migrations'

    def handle(self, *args, **options):
        self.stdout.write("Creating migrations...")
        call_command('makemigrations')
        self.stdout.write("Applying migrations...")
        call_command('migrate')
