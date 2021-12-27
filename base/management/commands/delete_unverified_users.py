from django.core.management.base import BaseCommand

from base.models import UninorteUser

# heroku cronun task manage this
""" UninorteUser.objects.filter(
    created_at__lte=timezone.now() - timedelta(weeks=1)
) """


class Command(BaseCommand):
    help = "Delete unverified users, those who registration process was manual"

    def handle(self, *args, **options):

        UninorteUser.objects.filter(verified=False).delete()
        self.stdout.write("Successfully deleted unverified users")
