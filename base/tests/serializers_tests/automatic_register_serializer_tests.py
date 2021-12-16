from django.test import TestCase

from base.data_factories import get_random_schedule
from base.models import UninorteUser
from base.serializers import AutomaticRegisterSerializer
from base.tests.test_utils import InstanceAssertionsMixin


class TestAutomaticRegisterSerializer(TestCase, InstanceAssertionsMixin):
    @classmethod
    def setUpTestData(cls):
        cls.user_to_filter = UninorteUser.objects.create(
            username="user1",
            schedule=get_random_schedule(),
        )

    def test_valid_serializer(self):

        # hour_index, day_index
        list_of_indices = [
            (0, 1),
            (1, 1),
            (1, 4),
            (2, 2),
            (2, 4),
            (3, 1),
            (8, 1),
            (8, 2),
            (8, 4),
            (9, 1),
            (9, 2),
            (9, 4),
            (10, 0),
            (10, 2),
            (11, 0),
            (11, 1),
            (11, 2),
        ]

        data = {"list_of_indices": list_of_indices, "username": "a_user"}

        serializer = AutomaticRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assert_instance_exists(UninorteUser, username="a_user")

    def test_hour_out_of_range(self):

        list_of_indices = [
            (0, 1),
            (1, 1),
            (1, 4),
            (13, 2),
        ]

        data = {"list_of_indices": list_of_indices, "username": "a_user"}

        serializer = AutomaticRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue("list_of_indices" in serializer.errors)

    def test_day_out_of_range(self):

        list_of_indices = [
            (0, 1),
            (1, 1),
            (1, 4),
            (1, 7),
        ]

        data = {"list_of_indices": list_of_indices, "username": "a_user"}

        serializer = AutomaticRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue("list_of_indices" in serializer.errors)

    def test_unique_username(self):

        list_of_indices = [
            (0, 1),
            (1, 1),
            (1, 4),
            (1, 2),
        ]

        data = {"list_of_indices": list_of_indices, "username": "user1"}

        serializer = AutomaticRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue("username" in serializer.errors)
