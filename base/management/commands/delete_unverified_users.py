from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from base.models import UninorteUser


class Command(BaseCommand):
    help = "Delete unverified users, those who registration process was manual"

    def handle(self, *args, **options):

        amount, _ = (
            UninorteUser.objects.filter(verified=False)
            .filter(created_at__lte=timezone.now() - timedelta(weeks=1))
            .delete()
        )
        self.stdout.write(f"Successfully deleted {amount} unverified users")
