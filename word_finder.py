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


def main(url, letter):
    words = read_url(url)
    matched_words = list()
    for word in run_permutation(letter, 5):
        for w in words:
            if word == w:
                matched_words.appened(word)
    return matched_words


if __name__ == '__main__':
    letters = 'qyipjzxcvn'
    url = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
    main(url, letters)
    
