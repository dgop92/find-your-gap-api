from base.core.constants import DAYS_PER_WEEK


def get_ss_from_list_of_indices(list_of_indices):
    ss_list = [0 for _ in range(98)]
    for day_hour in list_of_indices:
        day_index, hour_index = day_hour
        pos = hour_index * DAYS_PER_WEEK + day_index
        ss_list[pos] = 1
    return "".join(map(str, ss_list))
