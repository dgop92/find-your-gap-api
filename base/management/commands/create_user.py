from django.core.management.base import BaseCommand

from base.models import UninorteUser


class Command(BaseCommand):
    help = "create a uninorte user"

    def add_arguments(self, parser):

        parser.add_argument(
            "username",
            type=str,
        )

        parser.add_argument(
            "string_schedule",
            type=str,
        )

        parser.add_argument("verified", type=bool, default=False)

    def handle(self, *args, **options):
        try:
            UninorteUser.objects.create(
                username=options["username"],
                schedule=options["string_schedule"],
                schedule=options["verified"],
            )
        except Exception as e:
            self.stdout.write(str(e))
