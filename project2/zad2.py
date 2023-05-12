import sys
from itertools import tee, islice
from queue import Queue

from histogram import histogram
from words import words


def ngrams(words, count):
    prev = Queue(count)
    for word in words:
        if prev.full():
            yield tuple(prev.queue)
            prev.get()
        prev.put(word)


def bigrams_trigrams(file, n):
    bigram_words, trigram_words = tee(words(file), 2)
    bigrams = islice(histogram(ngrams(bigram_words, 2)), n)
    trigrams = islice(histogram(ngrams(trigram_words, 3)), n)
    return bigrams, trigrams


if __name__ == '__main__':
    bigrams, trigrams = bigrams_trigrams(sys.argv[1], int(sys.argv[2]))
    print('Bigrams:')
    for key, value in bigrams:
        print(f'{" ".join(key)}: {value}')
    print('\nTrigrams:')
    for key, value in trigrams:
        print(f'{" ".join(key)}: {value}')
