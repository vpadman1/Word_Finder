# test functions for only read_url and run_permutation:
import itertools
import ssl
import urllib.request



def read_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    words = list()
    with urllib.request.urlopen(url, context=ctx) as f:
        words.append(f.read())
    words = words[0].decode().split('\n')
    return words


def run_permutation(iterator, n):
    list1 = list()
    for i in itertools.permutations(iterator, n):
        list1.append(''.join(i))
    return list1


# TEST CASE FOR run_permutation
def test_run_permutation():
    assert run_permutation('abc', 2) == ['ab', 'ac', 'ba', 'bc', 'ca', 'cb']

    
# test case for read_url
def test_read_url():
    url = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    words = list()
    with urllib.request.urlopen(url, context=ctx) as f:
        words.append(f.read())
    words = words[0].decode().split('\n')
    assert read_url(url) == words

    
if __name__ == '__main__':
    #instantiate the test function
    test_run_permutation()
    test_read_url()