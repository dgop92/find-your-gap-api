import unittest

import numpy as np

from base.core.analyze_meetings import (
    get_schedule_meeting_data,
    get_sum_meeting_matrix,
    is_needed_to_ignore_hour,
)

string_schedule1 = "01000000100100001010001000000000000000000000000000000000011010001101001010000111000000000000000000"
string_schedule2 = "01000000111100011100001010000001000000000000100000010000010100011010001100000000100000000000000000"


class TesAnalyzeMeetings(unittest.TestCase):
    def test_get_sum_meeting_matrix(self):

        sum_matrix = get_sum_meeting_matrix([string_schedule1, string_schedule2])

        expected_matrix = [
            [0, 2, 0, 0, 0, 0, 0],
            [0, 2, 1, 1, 2, 0, 0],
            [0, 1, 2, 1, 1, 0, 0],
            [0, 2, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 2, 1, 1, 1, 0, 0],
            [1, 2, 1, 1, 1, 0, 0],
            [2, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]

        self.assertTrue(np.array_equal(sum_matrix, expected_matrix))

    def test_get_schedule_meeting_data(self):

        data = get_schedule_meeting_data([string_schedule1, string_schedule2])
        self.assertEqual(data["total_students"], 2)

        results = data["results"]

        hour1 = list(
            filter(lambda g: g["day_index"] == 1 and g["hour_index"] == 0, results)
        )[0]
        self.assertEqual(hour1["availability"], 0)
        self.assertEqual(hour1["number_of_students"], 0)

        hour2 = list(
            filter(lambda g: g["day_index"] == 1 and g["hour_index"] == 2, results)
        )[0]
        self.assertEqual(hour2["availability"], 0.5)
        self.assertEqual(hour2["number_of_students"], 1)

        hour3 = list(
            filter(lambda g: g["day_index"] == 0 and g["hour_index"] == 0, results)
        )[0]
        self.assertEqual(hour3["availability"], 1)
        self.assertEqual(hour3["number_of_students"], 2)

    def test_is_needed_to_ignore_hour(self):

        schedule = np.array(
            [
                [1, 1, 0, 1, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 1],
                [0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        )

        filter_schedule = "11010011000000100000000000000000000000001000000000000000001100000000000000000010000100100000000000"

        result = np.where(schedule == 1)
        idxs = list(zip(result[0], result[1]))

        for idx in idxs:
            self.assertTrue(is_needed_to_ignore_hour(filter_schedule, idx[0], idx[1]))

        result = np.where(schedule == 0)
        idxs = list(zip(result[0], result[1]))

        for idx in idxs:
            self.assertFalse(is_needed_to_ignore_hour(filter_schedule, idx[0], idx[1]))

    def test_get_schedule_meeting_data_with_filter(self):

        schedule = np.array(
            [
                [1, 1, 0, 1, 0],
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0],
            ]
        )

        filter_schedule = "11010011000000100000000000000000000000001000000000000000001100000000000000000010000100100000000000"

        idxs_np = np.where(schedule == 1)
        idxs = list(zip(idxs_np[0], idxs_np[1]))

        data = get_schedule_meeting_data(
            [string_schedule1, string_schedule2], filter_schedule
        )
        results = data["results"]

        for result in results:
            t = (result["hour_index"], result["day_index"])
            self.assertNotIn(t, idxs)

        idxs_np = np.where(schedule == 0)
        idxs = set(list(zip(idxs_np[0], idxs_np[1])))

        found_idxs = set(
            (result["hour_index"], result["day_index"]) for result in results
        )
        self.assertSetEqual(found_idxs, idxs)
