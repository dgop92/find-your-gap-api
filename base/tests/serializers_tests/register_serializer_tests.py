from django.test import TestCase
from django.test.utils import override_settings

from base.models import UninorteUser
from base.serializers import RegisterSerializer
from base.tests.test_utils import DATA_FUNC_TEMPLATE, InstanceAssertionsMixin

# test_schedule_2
string_schedule2 = "10000001100000000000000000000000000010000000000000000000000000000000000000000000000000010000001000"

string_schedule3 = "01000000111100011100001010000001000000000000100000010000010100011010001100000000100000000000000000"


class TestRegisterSerializer(TestCase, InstanceAssertionsMixin):
    @classmethod
    def setUpTestData(cls):
        UninorteUser.objects.create(
            username="user_rep",
            schedule=string_schedule3,
        )

    def test_valid_username(self):

        data = {
            "username": "some_username",
            "password": "password",
            "password_confirmation": "password",
        }

        users_serializers = RegisterSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())

    def test_invalid_length(self):

        data = {
            "username": "",
            "password": "password",
            "password_confirmation": "password",
        }

        users_serializers = RegisterSerializer(data=data)
        self.assertFalse(users_serializers.is_valid())
        self.assertTrue("username" in users_serializers.errors)

        data = {
            "username": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaau",
            "password": "password",
            "password_confirmation": "password",
        }

        users_serializers = RegisterSerializer(data=data)
        self.assertFalse(users_serializers.is_valid())
        self.assertTrue("username" in users_serializers.errors)

    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(4))
    def test_can_update_schedule(self):

        data = {
            "username": "user_rep",
            "password": "password",
            "password_confirmation": "password",
        }

        users_serializers = RegisterSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        users_serializers.save()
        self.assert_instance_exists(UninorteUser, username="user_rep")
        user = UninorteUser.objects.get(username="user_rep")
        self.assertEqual(user.schedule, string_schedule2)
        self.assertTrue(user.verified)

    def test_mismatch_password(self):

        data = {
            "username": "some_username",
            "password": "password",
            "password_confirmation": "no_same_password",
        }

        users_serializers = RegisterSerializer(data=data)
        self.assertFalse(users_serializers.is_valid())
        self.assertTrue("non_field_errors" in users_serializers.errors)

    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(4))
    def test_create_user(self):

        data = {
            "username": "some_username",
            "password": "password",
            "password_confirmation": "password",
        }

        users_serializers = RegisterSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        users_serializers.save()
        user = UninorteUser.objects.get(username="some_username")
        self.assert_instance_exists(UninorteUser, username="some_username")
        self.assertEqual(user.schedule, string_schedule2)
        self.assertTrue(user.verified)
