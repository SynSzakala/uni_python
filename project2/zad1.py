import sys

from histogram import histogram, Histogram
from words import words


def rank(histogram: Histogram, n):
    rank = []
    for key, value in histogram:
        if rank and value == rank[-1][1]:
            rank[-1][0].append(key)
        elif len(rank) == n:
            break
        else:
            rank.append(([key], value))

    return rank[:n]


def wordcount(file, n):
    return rank(histogram(words(file)), n)


if __name__ == '__main__':
    count = wordcount(sys.argv[1], int(sys.argv[2]))
    for keys, value in count:
        print(f'{",".join(keys)}: {value}')
