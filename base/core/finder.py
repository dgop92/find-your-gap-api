import numpy as np

from base.core.constants import BIT_MATRIX_DATA_TYPE, DAYS, HOURS, HOURS_PER_DAY
from base.core.distance_algorithms import get_distance_matrix_from_string_schedule

DEFAULT_MATRIX_COMPUTER_OPTIONS = {
    "compute_sd": False,
    "no_classes_day": False,
    "ignore_weekend": True,
}


class DistanceMatrixComputer:

    """
    Compute sum, average and standard deviation of all distances matrices

    """

    def __init__(self, distance_matrices, options=None):
        self.distance_matrices = distance_matrices
        if options:
            self.options = {**DEFAULT_MATRIX_COMPUTER_OPTIONS, **options}
        else:
            self.options = DEFAULT_MATRIX_COMPUTER_OPTIONS

        self.sum_matrix = None
        self.avg_matrix = None
        self.deviation_matrix = None

    def compute(self):
        if self.options["no_classes_day"]:
            self.set_to_one_no_classes_days()

        self.zerofication_of_matrices()

        self.sum_matrix = np.sum(self.distance_matrices, axis=0)
        self.avg_matrix = np.mean(self.distance_matrices, axis=0, dtype="float32")

        if self.options["compute_sd"]:
            self.deviation_matrix = np.std(
                self.distance_matrices, axis=0, dtype="float32"
            )

    def zerofication_of_matrices(self):
        zero_indices = set()
        for distance_matrix in self.distance_matrices:
            current_zero_indices = np.where(distance_matrix == 0)
            n = len(current_zero_indices[0])
            for i in range(n):
                zero_indices.add(
                    (current_zero_indices[0][i], current_zero_indices[1][i])
                )

        for distance_matrix in self.distance_matrices:
            for index_tuple in zero_indices:
                distance_matrix[index_tuple[0]][index_tuple[1]] = 0

    def set_to_one_no_classes_days(self):

        for distance_matrix in self.distance_matrices:
            transpose_matrix = distance_matrix.T
            for i, day in enumerate(transpose_matrix):
                if self.options["ignore_weekend"] and i > 4:
                    break

                has_no_classes = not any(day)
                if has_no_classes:
                    transpose_matrix[i] = np.ones(
                        HOURS_PER_DAY, dtype=BIT_MATRIX_DATA_TYPE
                    )

    def get_sum_matrix(self):
        return self.sum_matrix

    def get_avg_matrix(self):
        return self.avg_matrix

    def get_sd_matrix(self):
        return self.deviation_matrix


class GapFinder:

    """
    Find all gaps from a series of string schedules

    """

    def __init__(self, string_schedules, compute_sd=False):
        self.compute_sd = compute_sd
        self.string_schedules = string_schedules
        self.distance_matrices = list(
            map(get_distance_matrix_from_string_schedule, string_schedules)
        )
        self.distance_matrix_computer = DistanceMatrixComputer(
            self.distance_matrices, self.compute_sd
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
