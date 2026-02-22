import logging
import ssl
import urllib.request
from pathlib import Path

WORD_LIST_URL = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
_CACHE_FILE = Path(__file__).parent / '.word_cache.txt'

logging.basicConfig(
    filename='word_finder.log',
    level=logging.INFO,
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
)
log = logging.getLogger(__name__)


class WordFinder:
    def __init__(self, url=WORD_LIST_URL, n=5, use_cache=True):
        self.url = url
        self.n = n
        self.use_cache = use_cache

    def _load_words(self):
        """Return the word list from disk cache if available, otherwise fetch from URL."""
        if self.use_cache and _CACHE_FILE.exists():
            log.info("loading word list from disk cache: %s", _CACHE_FILE)
            return _CACHE_FILE.read_text().splitlines()

        log.info("fetching word list from %s", self.url)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(self.url, context=ctx) as f:
            content = f.read().decode()

        if self.use_cache:
            _CACHE_FILE.write_text(content)
            log.info("word list cached to %s", _CACHE_FILE)

        return content.splitlines()

    def find(self, letters):
        """Return all n-letter words from the word list formable from letters (repetition allowed).

        Algorithm: O(W * n) filter over the word list — where W is the number of
        words and n is the word length — instead of generating all L^n combinations
        first (L = number of distinct letters).  For the default inputs this is
        ~29 000 character checks vs 1 048 576 string constructions.
        """
        letter_set = set(letters)
        words = self._load_words()
        matches = [
            w for w in words
            if len(w) == self.n and all(c in letter_set for c in w)
        ]
        log.info("found %d matching words", len(matches))
        return matches


def main(url=WORD_LIST_URL, letters=None, n=5):
    finder = WordFinder(url=url, n=n)
    matched = finder.find(letters or [])
    print("matched words", matched)
    return matched


if __name__ == '__main__':
    letters = ['q', 'w', 'y', 'i', 'p', 'd', 'f', 'h', 'j', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
    main(letters=letters, n=5)
