from django.core.management.base import BaseCommand

from base.data_factories import get_random_user


class Command(BaseCommand):
    help = "create random users"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--number",
            type=int,
            default=10,
            help="Specify the number of students to create",
        )

        parser.add_argument(
            "--mult_number",
            type=int,
            default=1,
            help="Specify the number of students to create",
        )

    def handle(self, *args, **options):

        for i in range(options["number"]):
            user_id = (i + 1) * options["mult_number"]
            self.stdout.write(f"Creating user {user_id}")
            get_random_user(user_id)
