import numpy as np

from base.constants import (
    BIT_MATRIX_DATA_TYPE,
    DAYS,
    DAYS_PER_WEEK,
    HOURS,
    HOURS_PER_DAY,
    UNINORTE_SCHEDULE_SIZE,
)


class DistanceComputer:

    """
    Compute the distance between classes in each free hour (gap)

    Example:
    In a bit_matrix each column is a day, so given the the followng day
    [0, 0, 1, 1, 0, 0, 0, 1]

    The distance will be [2, 1, 0, 0, 1, 2, 1, 0], now the class hours are
    represented using a zero

    """

    def __init__(self, string_schedules):
        self.string_schedules = string_schedules
        self.distance_matrices = []

    def from_strings_schedules_to_distance_matrix(self):
        for string_schedule in self.string_schedules:
            bit_matrix = self.from_string_to_bit_matrix(string_schedule)
            self.apply_distance_to_bit_matrix(bit_matrix)
            self.distance_matrices.append(bit_matrix)

    def get_distance_matrices(self):
        return self.distance_matrices

    def from_string_to_bit_matrix(self, string_schedule):

        bit_matrix = np.zeros(shape=UNINORTE_SCHEDULE_SIZE, dtype=BIT_MATRIX_DATA_TYPE)

        for i, c in enumerate(string_schedule):
            if c == "1":
                i_index = i // DAYS_PER_WEEK
                j_index = i % DAYS_PER_WEEK
                bit_matrix[i_index][j_index] = 1

        return bit_matrix

    def apply_distance_to_bit_matrix(self, bit_matrix):

        transpose_bit_matrix = bit_matrix.T
        for day in transpose_bit_matrix:
            gaps = self.indices_of_sub_arrays_of_zeros(day)
            for gap in gaps:
                self.put_distance_to_day(*gap, day)

    # NOTE Improve Algorithm
    def indices_of_sub_arrays_of_zeros(self, arr):
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

    # NOTE Improve Algorithm
    def put_distance_to_day(self, start, end, day):
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


class DistanceMatrixComputer:

    """
    Compute sum, average and standard deviation of all distances matrices

    """

    def __init__(self, distance_matrices, compute_sd=False):
        self.distance_matrices = distance_matrices

        self.is_compute_sd_needed = compute_sd
        self.sum_matrix = np.zeros(shape=UNINORTE_SCHEDULE_SIZE, dtype="float32")
        self.avg_matrix = np.zeros(shape=UNINORTE_SCHEDULE_SIZE, dtype="float32")

        self.deviation_matrix = None

    def compute(self):
        self.compute_sum()
        self.compute_avg()

        if self.is_compute_sd_needed:
            self.compute_sd()

    def get_avg_matrix(self):
        return self.avg_matrix

    def get_sd_matrix(self):
        return self.deviation_matrix

    def compute_sum(self):
        for i in range(HOURS_PER_DAY):
            for j in range(DAYS_PER_WEEK):
                for current_distance_matrix in self.distance_matrices:
                    # if a zero is found, that means is class, so we must
                    # ignore this day-hour
                    if current_distance_matrix[i][j] == 0:
                        self.sum_matrix[i][j] = 0
                        break

                    self.sum_matrix[i][j] += current_distance_matrix[i][j]

    def compute_avg(self):
        self.avg_matrix = self.sum_matrix * (1 / len(self.distance_matrices))

    def compute_sd(self):

        self.deviation_matrix = np.zeros(shape=UNINORTE_SCHEDULE_SIZE, dtype="float32")

        for i in range(HOURS_PER_DAY):
            for j in range(DAYS_PER_WEEK):
                for current_distance_matrix in self.distance_matrices:
                    if current_distance_matrix[i][j] == 0:
                        self.sum_matrix[i][j] = 0
                        break

                    self.deviation_matrix[i][j] += (
                        current_distance_matrix[i][j] - self.avg_matrix[i][j]
                    ) ** 2

        self.deviation_matrix = self.deviation_matrix * (
            1 / len(self.distance_matrices)
        )
        self.deviation_matrix = np.sqrt(self.deviation_matrix)


class GapFinder:

    """
    Find all gaps from a series of string schedules

    """

    def __init__(self, string_schedules, compute_sd=False):
        self.compute_sd = compute_sd
        self.string_schedules = string_schedules
        self.distance_computer = DistanceComputer(string_schedules)
        self.distance_computer.from_strings_schedules_to_distance_matrix()
        self.distance_matrix_computer = DistanceMatrixComputer(
            self.distance_computer.get_distance_matrices(), self.compute_sd
        )
        self.distance_matrix_computer.compute()
        self.results = []

    def find_gaps(self):

        avg_matrix = self.distance_matrix_computer.get_avg_matrix()
        sd_matrix = self.distance_matrix_computer.get_sd_matrix()

        for i, hour in enumerate(HOURS):
            for j, day in enumerate(DAYS):
                if avg_matrix[i][j] != 0:

                    new_gap_item = {
                        "day": day,
                        "hour": hour,
                        "avg": float(avg_matrix[i][j]),
                    }

                    if sd_matrix is not None:

                        new_gap_item.update({"sd": float(sd_matrix[i][j])})

                    self.results.append(new_gap_item)

    def apply_filters(self, limit=None):

        if self.compute_sd:
            sort_func = lambda gap: (gap["avg"], gap["sd"])  # noqa: E731
        else:
            sort_func = lambda gap: gap["avg"]  # noqa: E731

        self.results.sort(key=sort_func)

        if limit:
            results_lenght = len(self.results)
            if results_lenght > limit:
                items_to_pop = results_lenght - limit
                for _ in range(items_to_pop):
                    self.results.pop()

    def get_results(self):
        return self.results
