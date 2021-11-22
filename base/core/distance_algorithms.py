import numpy as np

from base.core.constants import (
    BIT_MATRIX_DATA_TYPE,
    DAYS_PER_WEEK,
    UNINORTE_SCHEDULE_SIZE,
)


def indices_of_sub_arrays_of_zeros(arr):

    """
    Given an array of zeros and ones return a generator with
    the indices of the sub-arrays of zeros

    Example:

    Input: [0, 0, 0, 1, 1, 1, 0, 1, 0]
    Output: [(0, 3), (6, 7), (8, 9)]
    """

    prev = 0
    _next = 0

    while _next < len(arr):

        # Move both pointer until we find a free hour (0)
        while _next < len(arr):
            if arr[_next] == 1:
                arr[_next] = 0
                _next += 1
                prev += 1
            else:
                break

        # Move only next pointer until we find a class (1)
        # if there is a zero at the end increase by one
        while _next < len(arr):
            if arr[_next] == 0:
                _next += 1
            else:
                break

        if _next - prev > 0:
            yield prev, _next
            prev = _next


def put_distance_to_day(start, end, day):
    size_of_gap = end - start
    size_of_day_arr = len(day)

    if start == 0 and end == size_of_day_arr:
        day[start:end] = np.full(size_of_day_arr, 0, dtype=BIT_MATRIX_DATA_TYPE)
    elif start == 0:
        day[start:end] = [i for i in range(size_of_gap, 0, -1)]
    elif end == size_of_day_arr:
        day[start:end] = [i for i in range(1, size_of_gap + 1)]
    else:
        zeros = np.empty(size_of_gap, dtype=BIT_MATRIX_DATA_TYPE)
        half_point = size_of_gap // 2 + size_of_gap % 2
        # Case example of extra_even [1,2,2,1]
        extra_even = 1 ^ (size_of_gap % 2)
        p = 0
        # Acending
        for i in range(1, half_point + extra_even, 1):
            zeros[p] = i
            p += 1
        # Desending
        for i in range(half_point, 0, -1):
            zeros[p] = i
            p += 1
        day[start:end] = zeros


def apply_distance_to_bit_matrix(bit_matrix):

    transpose_bit_matrix = bit_matrix.T
    for day in transpose_bit_matrix:
        gaps = indices_of_sub_arrays_of_zeros(day)
        for gap in gaps:
            put_distance_to_day(*gap, day)


def from_string_to_bit_matrix(string_schedule):

    bit_matrix = np.zeros(shape=UNINORTE_SCHEDULE_SIZE, dtype=BIT_MATRIX_DATA_TYPE)

    for i, c in enumerate(string_schedule):
        if c == "1":
            i_index = i // DAYS_PER_WEEK
            j_index = i % DAYS_PER_WEEK
            bit_matrix[i_index][j_index] = 1

    return bit_matrix


def get_distance_matrix_from_string_schedule(string_schedule):

    """
    Compute the distance between classes in each free hour (gap)

    Example:
    In a bit_matrix each column is a day, so given the the followng day
    [0, 0, 1, 1, 0, 0, 0, 1]

    The distance will be [2, 1, 0, 0, 1, 2, 1, 0], now the class hours are
    represented using a zero

    """

    bit_matrix = from_string_to_bit_matrix(string_schedule)
    apply_distance_to_bit_matrix(bit_matrix)
    return bit_matrix
