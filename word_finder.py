import itertools
import logging as lg
import ssl
import urllib.request

import numpy as np


class word_finder:
    def __init__(self, url, iterator, n, filename):
        self.url = url
        self.iterator = iterator
        self.n = n
        self.filename = filename

    def logger(self, filename):
        lg.basicConfig(filename, level=lg.INFO,
                       format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    def read_url(self, url):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        words = list()
        with urllib.request.urlopen(self.url, context=ctx) as f:
            words.append(f.read())
        words = words[0].decode().split('\n')
        lg.info("words appended to the list from website")
        return words

    def run_combinations(self, iterator, n):
        list1 = list()
        for i in itertools.combinations(self.iterator, self.n):
            list1.append(''.join(i))
        lg.info("list containing different permutation of words")
        return list1


def main(url, input_string, n, filename):
    find_word = word_finder(url, input_string, 5, filename)
    words_from_website = np.array(find_word.read_url(url))
    words_from_choice = np.array(
        find_word.run_combinations(iterator=letters, n=5))
    final_words = np.intersect1d(words_from_choice, words_from_website)
    words_containing_i = [v for i, v in enumerate(
        final_words) if "i" in v if "c" in v]
    lg.info("final list of words for use")
    return print("words_containing_i", words_containing_i)


if __name__ == '__main__':
    letters = 'qyipjzxcvn'
    url = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
    filename = "/log.txt"
    main(url=url, input_string=letters, n=5, filename=filename)
