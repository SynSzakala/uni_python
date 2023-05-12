from typing import Iterable

Histogram = list[tuple[str, int]]


def histogram(seq: Iterable) -> Histogram:
    count = dict()
    for item in seq:
        if item in count:
            count[item] += 1
        else:
            count[item] = 1

    return sorted(count.items(), key=lambda it: it[1], reverse=True)
