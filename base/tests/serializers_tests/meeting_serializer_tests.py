from django.test import TestCase

from base.serializers import MeetingSerializer
from base.tests.data_factories import get_random_user
from base.tests.test_utils import create_inmemory_file

# test_schedule_2
string_schedule2 = "10000001100000000000000000000000000010000000000000000000000000000000000000000000000000010000001000"

string_schedule3 = "01000000111100011100001010000001000000000000100000010000010100011010001100000000100000000000000000"


class TestMeetingSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.set_of_schedules = set(
            [get_random_user(user_id=i).schedule for i in range(3)]
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
