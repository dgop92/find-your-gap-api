from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from base.data_factories import get_random_schedule
from base.models import UninorteUser
from base.tests.test_utils import InstanceAssertionsMixin


class DeleteUnverifiedUsers(TestCase, InstanceAssertionsMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = UninorteUser.objects.create(
            username="user1", schedule=get_random_schedule(), verified=False
        )
        cls.user2 = UninorteUser.objects.create(
            username="user2", schedule=get_random_schedule(), verified=True
        )
        cls.user3 = UninorteUser.objects.create(
            username="user3", schedule=get_random_schedule(), verified=False
        )

    def test_users_deletion(self):
        out = StringIO()
        call_command("delete_unverified_users", stdout=out)
        self.assert_instance_exists(UninorteUser, username="user2")
        self.assert_instance_does_not_exist(UninorteUser, username="user1")
        self.assert_instance_does_not_exist(UninorteUser, username="user3")
        self.assertIn("Successfully deleted unverified users", out.getvalue())
