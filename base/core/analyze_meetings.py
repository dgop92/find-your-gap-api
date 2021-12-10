import numpy as np

from base.core.constants import DAYS_PER_WEEK
from base.core.distance_algorithms import from_string_to_bit_matrix


def is_needed_to_ignore_hour(filter_schedule, i, j):
    if filter_schedule:
        pos = i * DAYS_PER_WEEK + j
        return bool(int(filter_schedule[pos]))

    return False


def get_sum_meeting_matrix(string_schedules):
    bit_matrices = np.array(list(map(from_string_to_bit_matrix, string_schedules)))
    return np.sum(bit_matrices, axis=0)


def get_schedule_meeting_data(string_schedules, filter_schedule=None):
    sum_matrix = get_sum_meeting_matrix(string_schedules)
    total_students = len(string_schedules)
    hours, days = sum_matrix.shape
    results = []
    for i in range(hours):
        for j in range(days):
            if j > 4 or is_needed_to_ignore_hour(filter_schedule, i, j):
                break

            # the number of students available at this time
            number_of_students = total_students - sum_matrix[i][j]
            availability = number_of_students / total_students
            results.append(
                {
                    "day_index": j,
                    "hour_index": i,
                    "number_of_students": number_of_students,
                    "availability": availability,
                }
            )

    return {"total_students": total_students, "results": results}
