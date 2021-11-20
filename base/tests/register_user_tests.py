from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status

from base.models import UninorteUser
from base.tests.test_utils import InstanceAssertionsMixin, TestsMixin
from base.urls import register_view_name


@override_settings(
    API_REGISTER_DATA_FUNC="base.tests.register_utils.get_api_register_data"
)
class TestRegister(TestsMixin, TestCase, InstanceAssertionsMixin):
    def setUp(self):
        self.init()
        self.register_url = reverse(register_view_name)

    def test_positive_register(self):

        data = {
            "username": "some_username",
            "password": "password",
            "password_confirmation": "password",
        }

        self.post(self.register_url, data=data, status_code=status.HTTP_201_CREATED)
        self.assert_instance_exists(UninorteUser, username="some_username")

    def test_mismatch_password(self):

        data = {
            "username": "some_username",
            "password": "password",
            "password_confirmation": "no_same_password",
        }

        self.post(self.register_url, data=data, status_code=status.HTTP_400_BAD_REQUEST)
        self.assert_instance_does_not_exist(UninorteUser, username="some_username")
