from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from base.tests.test_utils import TestsMixin
from base.urls import manual_register_view_name


class TestManualRegisterView(TestCase, TestsMixin):
    def setUp(self):
        self.init()
        self.manual_url = reverse(manual_register_view_name)

    def test_valid_response(self):

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

        self.post(
            self.manual_url,
            data=data,
            status_code=status.HTTP_201_CREATED,
        )

    def test_invalid_response(self):

        data = {}

        self.post(
            self.manual_url,
            data=data,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
