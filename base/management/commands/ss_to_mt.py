from django.core.management.base import BaseCommand, CommandError

from base.core.distance_algorithms import from_string_to_bit_matrix
from base.models import UninorteUser


class Command(BaseCommand):
    help = "inspect the string schedule using a matrix visualization"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="username to retrieve the string schedule",
        )

        parser.add_argument(
            "--string-schedule",
            type=str,
            default="",
            help="direct string schedule",
        )

    def handle(self, *args, **options):

        if options["username"] and options["string_schedule"]:
            raise CommandError("just provide one of options")

        string_schedule = options["string_schedule"]
        if options["username"]:
            user = UninorteUser.objects.get(username=options["username"])
            string_schedule = user.schedule

        if string_schedule:
            bit_matrix = from_string_to_bit_matrix(string_schedule)
            self.stdout.write(str(bit_matrix))
        else:
            raise CommandError("provide at least one of options")
