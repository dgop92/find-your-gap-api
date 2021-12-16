import unittest

from base.core.automatic_register import get_ss_from_list_of_indices


class TestAutomaticRegister(unittest.TestCase):
    def test_get_ss_from_list_of_indicies(self):

        expected_ss = "01000000100100001010001000000000000000000000000000000000011010001101001010000111000000000000000000"

        list_of_indicies = [
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

        ss = get_ss_from_list_of_indices(list_of_indicies)
        self.assertTrue(ss, expected_ss)
