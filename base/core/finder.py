import numpy as np

from base.constants import (
    DAYS,
    DAYS_PER_WEEK,
    HOURS,
    HOURS_PER_DAY,
    UNINORTE_SCHEDULE_SIZE,
)
from base.core.distance_algorithms import get_distance_matrix_from_string_schedule


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
