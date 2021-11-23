def sort_results(results, with_sd=False):
    if with_sd:
        return sorted(results, key=lambda gap: (gap["avg"], gap["sd"]))
    else:
        return sorted(results, key=lambda gap: gap["avg"])


def limit_results(results, limit=-1):
    if limit != -1:
        return results[:limit]
    return results


def filter_by_days(results, day_indices=None):
    if day_indices:
        return list(filter(lambda e: e["day_index"] in day_indices, results))
    return results
