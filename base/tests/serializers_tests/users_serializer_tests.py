from django.test import TestCase

from base.models import UninorteUser
from base.serializers import UsersSerializer

string_schedule1 = "01000000100100001010001000000000000000000000000000000000011010001101001010000111000000000000000000"
string_schedule2 = "01000000111100011100001010000001000000000000100000010000010100011010001100000000100000000000000000"

KNOWN_GAPS = set(
    [
        (0, 0),
        (0, 2),
        (0, 4),
        (1, 0),
        (2, 0),
        (3, 0),
        (3, 2),
        (3, 4),
        (4, 0),
        (4, 1),
        (4, 2),
        (4, 4),
        (5, 0),
        (5, 1),
        (5, 2),
        (5, 4),
        (6, 0),
        (6, 1),
        (6, 4),
        (7, 0),
        (7, 1),
        (7, 4),
        (8, 0),
        (10, 4),
        (11, 4),
        (12, 0),
        (12, 1),
        (12, 2),
        (12, 4),
        (13, 0),
        (13, 1),
        (13, 2),
        (13, 4),
    ]
)


class TestUsersSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        UninorteUser.objects.create(
            username="my_user_1",
            schedule=string_schedule1,
        )

        UninorteUser.objects.create(
            username="my_user_2",
            schedule=string_schedule2,
        )

    def test_valid_usernames(self):

        data = {"usernames": ["my_user_1", "my_user_2"]}

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())

    def test_invalid_usernames(self):

        data = {"usernames": ["my_user", "omy"]}

        users_serializers = UsersSerializer(data=data)
        self.assertFalse(users_serializers.is_valid())
        self.assertTrue("usernames" in users_serializers.errors)

    def test_invalid_length_of_usernames(self):

        data = {"usernames": ["my_user_1"]}

        users_serializers = UsersSerializer(data=data)
        self.assertFalse(users_serializers.is_valid())
        self.assertTrue("usernames" in users_serializers.errors)

    def test_valid_limit(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "limit": 3,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())

    def test_invalid_limit(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "limit": 1,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertFalse(users_serializers.is_valid())
        self.assertTrue("limit" in users_serializers.errors)

    def test_valid_filter_by_days(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "days_to_filter": [0, 1],
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())

    def test_invalid_filter_by_days(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "days_to_filter": [8, -1],
        }

        users_serializers = UsersSerializer(data=data)
        self.assertFalse(users_serializers.is_valid())
        self.assertTrue("days_to_filter" in users_serializers.errors)

    def test_results(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]
        number_of_gaps = results["count"]
        found_gaps_indices = set(map(lambda e: (e["hour_index"], e["day_index"]), gaps))

        self.assertEqual(number_of_gaps, len(KNOWN_GAPS))
        self.assertSetEqual(found_gaps_indices, KNOWN_GAPS)

    def test_results_with_options(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "days_to_filter": [0, 1],
            "limit": 5,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]
        found_gaps_indices = set(map(lambda e: (e["hour_index"], e["day_index"]), gaps))

        self.assertEqual(len(found_gaps_indices), 5)
        for gap_index_tuple in found_gaps_indices:
            self.assertTrue(gap_index_tuple[1] == 0 or gap_index_tuple[1] == 1)

    def test_results_with_sd(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "compute_sd": True,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]

        self.assertTrue("sd" in gaps[0])

    def test_results_without_sd(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "compute_sd": False,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]

        self.assertTrue("sd" not in gaps[0])

    def test_results_with_no_classes_day(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "no_classes_day": True,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]
        found_gaps_indices = map(lambda e: e["day_index"], gaps)
        gaps_on_thursday = any(map(lambda e: e == 3, found_gaps_indices))
        self.assertTrue(gaps_on_thursday)

    def test_results_without_no_classes_day(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "no_classes_day": False,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]
        found_gaps_indices = map(lambda e: e["day_index"], gaps)
        gaps_on_thursday = any(map(lambda e: e == 3, found_gaps_indices))
        self.assertFalse(gaps_on_thursday)

    def test_results_with_ignore_weekend_to_false(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "ignore_weekend": False,
            "no_classes_day": True,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]
        found_gaps_indices = map(lambda e: e["day_index"], gaps)
        gaps_on_weekend = any(map(lambda e: e == 5 or e == 6, found_gaps_indices))
        self.assertTrue(gaps_on_weekend)

    def test_results_with_ignore_weekend_to_true(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "ignore_weekend": False,
            "no_classes_day": False,
        }

        users_serializers = UsersSerializer(data=data)
        self.assertTrue(users_serializers.is_valid())
        results = users_serializers.save()
        gaps = results["gaps"]
        found_gaps_indices = map(lambda e: e["day_index"], gaps)
        gaps_on_weekend = any(map(lambda e: e == 5 or e == 6, found_gaps_indices))
        self.assertFalse(gaps_on_weekend)
