from django.test import TestCase

from base.data_factories import get_random_user
from base.models import UninorteUser
from base.serializers import MeetingSerializer
from base.tests.test_utils import create_inmemory_file

# test_schedule_2
string_schedule2 = "10000001100000000000000000000000000010000000000000000000000000000000000000000000000000010000001000"


class TestMeetingSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.set_of_schedules = set(
            [get_random_user(user_id=i).schedule for i in range(3)]
        )
        cls.user_to_filter = UninorteUser.objects.create(
            username="u_filter",
            schedule=string_schedule2,
        )

    def test_valid_meeting_serializer(self):

        usernames_file = create_inmemory_file(content=b"my_user_0\nmy_user_1")

        data = {"usernames_file": usernames_file, "extra_usernames": ["my_user_2"]}

        meeting_serializer = MeetingSerializer(data=data)
        self.assertTrue(meeting_serializer.is_valid())

        validated_data = meeting_serializer.validated_data
        self.assertSetEqual(set(validated_data["final_ss"]), self.set_of_schedules)

        usernames_file.close()

    def test_no_source_of_usernames(self):

        meeting_serializer = MeetingSerializer(data={})
        self.assertFalse(meeting_serializer.is_valid())
        self.assertTrue("non_field_errors" in meeting_serializer.errors)

    def test_invalid_extension(self):

        usernames_file = create_inmemory_file(
            file_name="tmp.png", content=b"hello\npedro"
        )

        data = {"usernames_file": usernames_file}

        meeting_serializer = MeetingSerializer(data=data)
        self.assertFalse(meeting_serializer.is_valid())
        self.assertTrue("usernames_file" in meeting_serializer.errors)

        usernames_file.close()

    def test_big_file(self):

        usernames_file = create_inmemory_file(content=b"u" * 20000)

        data = {"usernames_file": usernames_file}

        meeting_serializer = MeetingSerializer(data=data)
        self.assertFalse(meeting_serializer.is_valid())
        self.assertTrue("usernames_file" in meeting_serializer.errors)

        usernames_file.close()

    def test_empty_file(self):

        usernames_file = create_inmemory_file()

        data = {"usernames_file": usernames_file}

        meeting_serializer = MeetingSerializer(data=data)
        self.assertFalse(meeting_serializer.is_valid())
        self.assertTrue("usernames_file" in meeting_serializer.errors)

        usernames_file.close()

    def test_allow_empty_list_of_extra_usernames(self):

        usernames_file = create_inmemory_file(
            content=b"my_user_0\nmy_user_1\nmy_user_2"
        )

        data = {"usernames_file": usernames_file, "extra_usernames": []}

        meeting_serializer = MeetingSerializer(data=data)
        self.assertTrue(meeting_serializer.is_valid())

    def test_not_enough_usernames(self):

        usernames_file = create_inmemory_file(content=b"my_user_0\nmy_user_5")

        data = {"usernames_file": usernames_file, "extra_usernames": ["my_user_10"]}

        meeting_serializer = MeetingSerializer(data=data)
        self.assertFalse(meeting_serializer.is_valid())
        self.assertTrue("non_field_errors" in meeting_serializer.errors)

    def test_invalid_username_to_filter(self):

        data = {
            "extra_usernames": ["my_user_0", "my_user_1"],
            "username_to_filter": "random",
        }

        meeting_serializer = MeetingSerializer(data=data)
        self.assertFalse(meeting_serializer.is_valid())
        self.assertTrue("username_to_filter" in meeting_serializer.errors)

    def test_hours_filtered_by_user(self):

        data = {
            "extra_usernames": ["my_user_0", "my_user_1"],
            "username_to_filter": self.user_to_filter.username,
        }

        meeting_serializer = MeetingSerializer(data=data)
        self.assertTrue(meeting_serializer.is_valid())
        data = meeting_serializer.save()
        results = data["results"]

        filtered_index = set([(0, 0), (1, 0), (1, 1), (5, 1), (12, 3), (13, 3)])

        for result in results:
            current_index_tuple = (result["hour_index"], result["day_index"])
            self.assertTrue(current_index_tuple not in filtered_index)
