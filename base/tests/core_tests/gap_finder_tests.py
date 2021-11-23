import unittest

from base.core.distance_algorithms import get_distance_matrix_from_string_schedule
from base.core.finder import DistanceMatrixComputer, GapFinder

string_schedule1 = "01000000100100001010001000000000000000000000000000000000011010001101001010000111000000000000000000"
string_schedule2 = "01000000111100011100001010000001000000000000100000010000010100011010001100000000100000000000000000"


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
