import unittest

import numpy as np

from base.core.distance_algorithms import (
    apply_distance_to_bit_matrix,
    from_string_to_bit_matrix,
    get_distance_matrix_from_string_schedule,
    indices_of_sub_arrays_of_zeros,
    put_distance_to_day,
)
from base.core.finder import DistanceMatrixComputer, GapFinder
from base.core.gap_filters import filter_by_days, limit_results, sort_results

string_schedule1 = "01000000100100001010001000000000000000000000000000000000011010001101001010000111000000000000000000"
string_schedule2 = "01000000111100011100001010000001000000000000100000010000010100011010001100000000100000000000000000"


class TestDistanceAlgorithms(unittest.TestCase):
    def test_indices_of_sub_arrays_of_zeros(self):

        arr = [0, 0, 0, 1, 1, 1, 0, 1, 0]
        indices = list(indices_of_sub_arrays_of_zeros(arr))
        self.assertListEqual(indices, [(0, 3), (6, 7), (8, 9)])
        print(indices)

        arr = [0, 1, 0, 1, 1, 1]
        indices = list(indices_of_sub_arrays_of_zeros(arr))
        self.assertListEqual(indices, [(0, 1), (2, 3)])

        arr = [0, 1, 1, 1, 1, 1]
        indices = list(indices_of_sub_arrays_of_zeros(arr))
        self.assertNotEqual(indices, [(0, 1), (2, 3)])

    def test_put_distance_to_day(self):

        arr = [0, 0, 0, 1, 1, 1, 0, 1, 0]
        put_distance_to_day(0, 3, arr)
        print(arr)
        self.assertListEqual(arr, [3, 2, 1, 1, 1, 1, 0, 1, 0])

        arr = [0, 0, 1, 1, 0, 1, 1, 0, 0]
        indices = list(indices_of_sub_arrays_of_zeros(arr))
        for gap in indices:
            put_distance_to_day(*gap, arr)
        print(arr)
        self.assertListEqual(arr, [2, 1, 0, 0, 1, 0, 0, 1, 2])

    def test_from_string_to_bit_matrix(self):

        bit_matrix = from_string_to_bit_matrix(string_schedule1)
        expected_matrix = np.array(
            [
                [0, 1, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 1, 0, 0],
                [0, 1, 1, 0, 1, 0, 0],
                [1, 0, 1, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        )
        self.assertEqual(np.array_equal(bit_matrix, expected_matrix), True)

        bit_matrix = from_string_to_bit_matrix(string_schedule2)
        expected_matrix = np.array(
            [
                [0, 1, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0],
                [1, 1, 0, 1, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        )
        self.assertEqual(np.array_equal(bit_matrix, expected_matrix), True)

    def test_apply_distance_to_bit_matrix(self):

        bit_matrix = from_string_to_bit_matrix(string_schedule1)
        apply_distance_to_bit_matrix(bit_matrix)
        expected_matrix = np.array(
            [
                [10, 0, 2, 0, 1, 0, 0],
                [9, 0, 1, 0, 0, 0, 0],
                [8, 1, 0, 0, 0, 0, 0],
                [7, 0, 1, 0, 1, 0, 0],
                [6, 1, 2, 0, 2, 0, 0],
                [5, 2, 3, 0, 3, 0, 0],
                [4, 2, 2, 0, 2, 0, 0],
                [3, 1, 1, 0, 1, 0, 0],
                [2, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 2, 0, 0],
                [1, 1, 1, 0, 3, 0, 0],
                [2, 2, 2, 0, 4, 0, 0],
            ]
        )
        self.assertEqual(np.array_equal(bit_matrix, expected_matrix), True)

        bit_matrix = from_string_to_bit_matrix(string_schedule2)
        apply_distance_to_bit_matrix(bit_matrix)
        expected_matrix = np.array(
            [
                [9, 0, 1, 1, 1, 0, 0],
                [8, 0, 0, 0, 0, 0, 0],
                [7, 0, 0, 0, 1, 0, 0],
                [6, 0, 1, 0, 2, 0, 0],
                [5, 1, 2, 0, 3, 0, 0],
                [4, 2, 1, 1, 4, 0, 0],
                [3, 2, 0, 2, 5, 0, 0],
                [2, 1, 0, 1, 6, 0, 0],
                [1, 0, 1, 0, 7, 0, 0],
                [0, 0, 2, 0, 8, 0, 0],
                [0, 0, 3, 1, 9, 0, 0],
                [1, 1, 4, 0, 10, 0, 0],
                [2, 2, 5, 1, 11, 0, 0],
                [3, 3, 6, 2, 12, 0, 0],
            ]
        )
        self.assertEqual(np.array_equal(bit_matrix, expected_matrix), True)


class TestMatrixComputer(unittest.TestCase):
    def test_set_to_one_no_classes_days_default_options(self):
        distance_matrix = get_distance_matrix_from_string_schedule(string_schedule1)
        dc = DistanceMatrixComputer([distance_matrix])
        dc.set_to_one_no_classes_days()

        expected_matrix = np.array(
            [
                [10, 0, 2, 1, 1, 0, 0],
                [9, 0, 1, 1, 0, 0, 0],
                [8, 1, 0, 1, 0, 0, 0],
                [7, 0, 1, 1, 1, 0, 0],
                [6, 1, 2, 1, 2, 0, 0],
                [5, 2, 3, 1, 3, 0, 0],
                [4, 2, 2, 1, 2, 0, 0],
                [3, 1, 1, 1, 1, 0, 0],
                [2, 0, 0, 1, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 1, 1, 0, 0],
                [0, 0, 0, 1, 2, 0, 0],
                [1, 1, 1, 1, 3, 0, 0],
                [2, 2, 2, 1, 4, 0, 0],
            ]
        )

        self.assertEqual(np.array_equal(dc.distance_matrices[0], expected_matrix), True)

    def test_set_to_one_no_classes_days_with_weekends(self):
        distance_matrix = get_distance_matrix_from_string_schedule(string_schedule1)
        dc = DistanceMatrixComputer(
            [distance_matrix], options={"ignore_weekend": False}
        )
        dc.set_to_one_no_classes_days()

        expected_matrix = np.array(
            [
                [10, 0, 2, 1, 1, 1, 1],
                [9, 0, 1, 1, 0, 1, 1],
                [8, 1, 0, 1, 0, 1, 1],
                [7, 0, 1, 1, 1, 1, 1],
                [6, 1, 2, 1, 2, 1, 1],
                [5, 2, 3, 1, 3, 1, 1],
                [4, 2, 2, 1, 2, 1, 1],
                [3, 1, 1, 1, 1, 1, 1],
                [2, 0, 0, 1, 0, 1, 1],
                [1, 0, 0, 1, 0, 1, 1],
                [0, 1, 0, 1, 1, 1, 1],
                [0, 0, 0, 1, 2, 1, 1],
                [1, 1, 1, 1, 3, 1, 1],
                [2, 2, 2, 1, 4, 1, 1],
            ]
        )

        self.assertEqual(np.array_equal(dc.distance_matrices[0], expected_matrix), True)

    def test_zerofication_of_matrices(self):
        distance_matrices = list(
            map(
                get_distance_matrix_from_string_schedule,
                [string_schedule1, string_schedule2],
            )
        )

        dc = DistanceMatrixComputer(distance_matrices)
        dc.zerofication_of_matrices()

        first_matrix = np.array(
            [
                [10, 0, 2, 0, 1, 0, 0],
                [9, 0, 0, 0, 0, 0, 0],
                [8, 0, 0, 0, 0, 0, 0],
                [7, 0, 1, 0, 1, 0, 0],
                [6, 1, 2, 0, 2, 0, 0],
                [5, 2, 3, 0, 3, 0, 0],
                [4, 2, 0, 0, 2, 0, 0],
                [3, 1, 0, 0, 1, 0, 0],
                [2, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 2, 0, 0],
                [1, 1, 1, 0, 3, 0, 0],
                [2, 2, 2, 0, 4, 0, 0],
            ]
        )
        second_matrix = np.array(
            [
                [9, 0, 1, 0, 1, 0, 0],
                [8, 0, 0, 0, 0, 0, 0],
                [7, 0, 0, 0, 0, 0, 0],
                [6, 0, 1, 0, 2, 0, 0],
                [5, 1, 2, 0, 3, 0, 0],
                [4, 2, 1, 0, 4, 0, 0],
                [3, 2, 0, 0, 5, 0, 0],
                [2, 1, 0, 0, 6, 0, 0],
                [1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 9, 0, 0],
                [0, 0, 0, 0, 10, 0, 0],
                [2, 2, 5, 0, 11, 0, 0],
                [3, 3, 6, 0, 12, 0, 0],
            ]
        )

        self.assertEqual(np.array_equal(dc.distance_matrices[0], first_matrix), True)
        self.assertEqual(np.array_equal(dc.distance_matrices[1], second_matrix), True)

    def test_sum_matrix_with_default_options(self):
        distance_matrices = list(
            map(
                get_distance_matrix_from_string_schedule,
                [string_schedule1, string_schedule2],
            )
        )

        dc = DistanceMatrixComputer(distance_matrices)
        dc.compute()

        expected_matrix = np.array(
            [
                [19, 0, 3, 0, 2, 0, 0],
                [17, 0, 0, 0, 0, 0, 0],
                [15, 0, 0, 0, 0, 0, 0],
                [13, 0, 2, 0, 3, 0, 0],
                [11, 2, 4, 0, 5, 0, 0],
                [9, 4, 4, 0, 7, 0, 0],
                [7, 4, 0, 0, 7, 0, 0],
                [5, 2, 0, 0, 7, 0, 0],
                [3, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 10, 0, 0],
                [0, 0, 0, 0, 12, 0, 0],
                [3, 3, 6, 0, 14, 0, 0],
                [5, 5, 8, 0, 16, 0, 0],
            ]
        )

        self.assertEqual(np.array_equal(dc.get_sum_matrix(), expected_matrix), True)

    def test_avg_matrix_with_default_options(self):
        distance_matrices = list(
            map(
                get_distance_matrix_from_string_schedule,
                [string_schedule1, string_schedule2],
            )
        )

        dc = DistanceMatrixComputer(distance_matrices)
        dc.compute()

        expected_matrix = np.array(
            [
                [9.5, 0.0, 1.5, 0.0, 1.0, 0.0, 0.0],
                [8.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [7.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [6.5, 0.0, 1.0, 0.0, 1.5, 0.0, 0.0],
                [5.5, 1.0, 2.0, 0.0, 2.5, 0.0, 0.0],
                [4.5, 2.0, 2.0, 0.0, 3.5, 0.0, 0.0],
                [3.5, 2.0, 0.0, 0.0, 3.5, 0.0, 0.0],
                [2.5, 1.0, 0.0, 0.0, 3.5, 0.0, 0.0],
                [1.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 6.0, 0.0, 0.0],
                [1.5, 1.5, 3.0, 0.0, 7.0, 0.0, 0.0],
                [2.5, 2.5, 4.0, 0.0, 8.0, 0.0, 0.0],
            ]
        )

        self.assertEqual(np.array_equal(dc.get_avg_matrix(), expected_matrix), True)

    def test_sd_matrix(self):

        distance_matrices = list(
            map(
                get_distance_matrix_from_string_schedule,
                [string_schedule1, string_schedule2],
            )
        )

        expected_matrix = np.array(
            [
                [0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 1.0, 0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0, 1.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0, 2.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 0.0],
                [0.5, 0.5, 2.0, 0.0, 4.0, 0.0, 0.0],
                [0.5, 0.5, 2.0, 0.0, 4.0, 0.0, 0.0],
            ]
        )

        dc = DistanceMatrixComputer(distance_matrices, options={"compute_sd": True})
        dc.compute()

        self.assertEqual(np.array_equal(dc.get_sd_matrix(), expected_matrix), True)


class TestGapFilters(unittest.TestCase):
    def test_sort_results(self):

        # testing, not all the values in gap item are included
        test_gaps = [
            {
                "avg": 1.5,
                "sd": 1.0,
                "day_index": 0,
                "hour_index": 6,
            },
            {
                "avg": 2.5,
                "sd": 2.0,
                "day_index": 2,
                "hour_index": 3,
            },
            {
                "avg": 1.0,
                "sd": 0.5,
                "day_index": 1,
                "hour_index": 1,
            },
        ]

        results = sort_results(test_gaps, with_sd=False)
        self.assertListEqual(list(map(lambda e: e["day_index"], results)), [1, 0, 2])

    def test_sort_results_with_sd(self):

        test_gaps = [
            {
                "avg": 1.0,
                "sd": 1.5,
                "day_index": 0,
                "hour_index": 6,
            },
            {
                "avg": 2.5,
                "sd": 2.0,
                "day_index": 2,
                "hour_index": 3,
            },
            {
                "avg": 1.0,
                "sd": 2.0,
                "day_index": 1,
                "hour_index": 1,
            },
        ]

        results = sort_results(test_gaps, with_sd=True)
        self.assertListEqual(list(map(lambda e: e["day_index"], results)), [0, 1, 2])

    def test_limit_results(self):

        test_gaps = [
            {
                "day_index": 0,
                "hour_index": 6,
            },
            {
                "day_index": 2,
                "hour_index": 3,
            },
            {
                "day_index": 1,
                "hour_index": 1,
            },
        ]

        results = limit_results(test_gaps, limit=-1)
        self.assertListEqual(list(map(lambda e: e["day_index"], results)), [0, 2, 1])
        results = limit_results(test_gaps, limit=1)
        self.assertListEqual(list(map(lambda e: e["day_index"], results)), [0])

    def test_filter_by_days(self):

        test_gaps = [
            {
                "day_index": 0,
                "hour_index": 6,
            },
            {
                "day_index": 2,
                "hour_index": 3,
            },
            {
                "day_index": 1,
                "hour_index": 11,
            },
            {
                "day_index": 1,
                "hour_index": 12,
            },
        ]

        results = filter_by_days(test_gaps, day_indices=[1, 0])
        filtered_results = set(map(lambda e: e["hour_index"], results))
        self.assertSetEqual(filtered_results, set([11, 12, 6]))

        results = filter_by_days(test_gaps, day_indices=[1, 0])
        filtered_results = set(map(lambda e: e["hour_index"], results))
        self.assertSetEqual(filtered_results, set([11, 12, 6]))


class TestGapFinder(unittest.TestCase):
    def test_find_gaps(self):
        distance_matrices = list(
            map(
                get_distance_matrix_from_string_schedule,
                [string_schedule1, string_schedule2],
            )
        )
        distance_matrix_computer = DistanceMatrixComputer(distance_matrices)

        gap_finder = GapFinder(distance_matrix_computer)
        gap_finder.find_gaps()

        expected_gaps = set(
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

        gaps_found = set(
            map(lambda e: (e["hour_index"], e["day_index"]), gap_finder.get_results())
        )

        self.assertSetEqual(gaps_found, expected_gaps)
