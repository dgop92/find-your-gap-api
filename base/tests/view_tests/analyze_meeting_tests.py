from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from base.tests.data_factories import get_random_user
from base.tests.test_utils import TestsMixin, create_inmemory_file
from base.urls import analyze_view_name

# test_schedule_2
string_schedule2 = "10000001100000000000000000000000000010000000000000000000000000000000000000000000000000010000001000"

string_schedule3 = "01000000111100011100001010000001000000000000100000010000010100011010001100000000100000000000000000"


class TestAnalyzeMeetingView(TestCase, TestsMixin):
    @classmethod
    def setUpTestData(cls):
        cls.set_of_schedules = set(
            [get_random_user(user_id=i).schedule for i in range(3)]
        )

    def setUp(self):
        self.init()
        self.analyze_url = reverse(analyze_view_name)

    def test_valid_response(self):

        usernames_file = create_inmemory_file(content=b"my_user_0\nmy_user_1")

        data = {"usernames_file": usernames_file, "extra_usernames": ["my_user_2"]}

        self.print_output = False
        self.post(
            self.analyze_url,
            multipart=True,
            data=data,
            status_code=status.HTTP_200_OK,
        )

        usernames_file.close()

    def test_valid_response_with_no_file(self):

        data = {"extra_usernames": ["my_user_0", "my_user_1"]}

        self.print_output = False
        self.post(
            self.analyze_url,
            data=data,
            status_code=status.HTTP_200_OK,
        )

    def test_invalid_response(self):

        data = {"extra_usernames": ["my_user_0"]}

        self.post(
            self.analyze_url,
            data=data,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
