import numpy as np
from django.test import TestCase, override_settings

from base.core.register_user import (
    APIUserRegister,
    RegisterUserError,
    StringScheduleProcessor,
)
from base.tests.test_utils import DATA_FUNC_TEMPLATE

DUMMY_REQUEST_DATA = {
    "username": "some_username",
    "password": "password",
}


class TestAPIUserRegister(TestCase):
    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(1))
    def test_200_full_uninorte_schedule(self):

        aur = APIUserRegister(DUMMY_REQUEST_DATA)
        aur.find_full_uninorte_schedule()
        self.assertTrue(bool(aur.uninorte_schedule))

    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(2))
    def test_401_full_uninorte_schedule(self):

        aur = APIUserRegister(DUMMY_REQUEST_DATA)

        with self.assertRaises(RegisterUserError) as cm:
            aur.find_full_uninorte_schedule()

        self.assertEqual(str(cm.exception), aur.unauthorized_message)
        self.assertFalse(bool(aur.uninorte_schedule))

    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(3))
    def test_500_full_uninorte_schedule(self):

        aur = APIUserRegister(DUMMY_REQUEST_DATA)

        with self.assertRaises(RegisterUserError) as cm:
            aur.find_full_uninorte_schedule()

        self.assertEqual(str(cm.exception), aur.unexpected_message)
        self.assertFalse(bool(aur.uninorte_schedule))

    def test_is_two_hours_block(self):

        input_data = [
            {
                "start_time_string": "10:30 AM",
                "end_time_string": "12:28 PM",
            },
            {
                "start_time_string": "6:30 AM",
                "end_time_string": "8:28 AM",
            },
            {
                "start_time_string": "2:30 PM",
                "end_time_string": "4:28 PM",
            },
            {
                "start_time_string": "11:30 AM",
                "end_time_string": "1:28 PM",
            },
        ]

        for data in input_data:
            self.assertTrue(
                APIUserRegister.is_two_hours_block(
                    data["start_time_string"], data["end_time_string"]
                )
            )

    def test_is_one_hour_block(self):

        input_data = [
            {
                "start_time_string": "11:30 AM",
                "end_time_string": "12:28 PM",
            },
            {
                "start_time_string": "7:30 AM",
                "end_time_string": "8:28 AM",
            },
            {
                "start_time_string": "3:30 PM",
                "end_time_string": "4:28 PM",
            },
            {
                "start_time_string": "11:30 AM",
                "end_time_string": "12:28 PM",
            },
        ]

        for data in input_data:
            self.assertFalse(
                APIUserRegister.is_two_hours_block(
                    data["start_time_string"], data["end_time_string"]
                )
            )

    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(4))
    def test_get_class_hours(self):

        aur = APIUserRegister(DUMMY_REQUEST_DATA)
        class_hours_set = set(aur.get_class_hours())
        expected_class_hours_set = set(
            [(0, 0), (1, 0), (5, 1), (1, 1), (12, 3), (13, 3)]
        )
        self.assertSetEqual(class_hours_set, expected_class_hours_set)

    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(4))
    def test_invalid_get_class_hours(self):

        aur = APIUserRegister(DUMMY_REQUEST_DATA)
        class_hours_set = set(aur.get_class_hours())
        expected_class_hours_set = set(
            [(0, 0), (6, 0), (5, 1), (1, 1), (2, 3), (13, 3)]
        )
        self.assertNotEqual(class_hours_set, expected_class_hours_set)


class TestStringScheduleProcessor(TestCase):
    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(4))
    def test_build_bit_matrix(self):

        aur = APIUserRegister(DUMMY_REQUEST_DATA)
        sc = StringScheduleProcessor(aur)
        sc.class_hours = aur.get_class_hours()
        sc.build_bit_matrix()

        expected_matrix = np.array(
            [
                [1, 0, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
            ]
        )

        self.assertTrue(np.array_equal(sc.bit_matrix, expected_matrix))

    @override_settings(SCHEDULE_DATA_FUNCTION=DATA_FUNC_TEMPLATE.format(4))
    def test_find_user_string_schedule(self):

        aur = APIUserRegister(DUMMY_REQUEST_DATA)
        sc = StringScheduleProcessor(aur)
        sc.find_user_string_schedule()

        expected_string_schedule = "10000001100000000000000000000000000010000000000000000000000000000000000000000000000000010000001000"

        self.assertEqual(sc.string_schedule, expected_string_schedule)
