import json

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status

from base.models import UninorteUser
from base.tests.test_utils import InstanceAssertionsMixin, TestsMixin
from base.urls import register_view_name


def get_schedule_data_1(username, password):
    route = "base/tests/test_data/test_schedule_1.json"
    with open(route, "r", encoding="utf8") as read_file:
        return 200, json.load(read_file)


DATA_FUNC_TEMPLATE = "base.tests.core_tests.register_user_tests.get_schedule_data_{0}"


@override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(1))
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
