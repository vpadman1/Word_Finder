# CLAUDE.md

This file provides guidance for AI assistants working in the Word_Finder repository.

## Project Overview

Word_Finder is a single-file Python utility that finds valid English words formable from a given set of letters. It works by:
1. Fetching a word list from Stanford's SGB (Stanford GraphBase) dataset over HTTPS
2. Generating all permutations of a supplied letter set using `itertools.product`
3. Finding the intersection of both sets using NumPy's `intersect1d`

The result is the subset of real English words that can be spelled using the chosen letters (with repetition allowed, since `itertools.product` is used rather than `itertools.permutations`).

## Repository Structure

```
Word_Finder/
├── CLAUDE.md        # This file
├── README.md        # Brief function-level description
└── word_finder.py   # Entire application — one file, ~53 lines
```

There are no subdirectories, no test suite, no CI configuration, and no packaging files.

## Dependencies

| Dependency | Source      | Purpose                              |
|------------|-------------|--------------------------------------|
| `numpy`    | PyPI        | `np.intersect1d` for set intersection|
| `itertools`| stdlib      | `itertools.product` for permutations |
| `logging`  | stdlib      | Log messages (partially broken)      |
| `ssl`      | stdlib      | Custom SSL context (cert check off)  |
| `urllib.request` | stdlib | Fetch word list from URL           |

There is no `requirements.txt`. If you add one, pin numpy: `numpy>=1.20`.

## Running the Script

```bash
python word_finder.py
```

The entry point hard-codes a letter set and URL:

```python
letters = ['q','w','y','i','p','d','f','h','j','z','x','c','v','b','n','m']
url = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
filename = "/log.txt"
main(url=url, input_string=letters, n=5, filename=filename)
```

Change `letters` in `word_finder.py:50` to alter the input set.

## Code Architecture

### Class: `word_finder` (`word_finder.py:8`)

| Method | Signature | Purpose |
|---|---|---|
| `__init__` | `(url, iterator, n, filename)` | Stores config on instance |
| `logger` | `(filename)` | Intended to configure `logging.basicConfig` |
| `read_url` | `(url)` | Fetches and decodes the Stanford word list |
| `run_combinations` | `(iterator, n)` | Returns all `n`-length products of `iterator` |

### Function: `main` (`word_finder.py:42`)

Instantiates `word_finder`, fetches the word list, generates combinations, finds their intersection, and prints the result.

### Entry Point (`word_finder.py:49-53`)

Sets hard-coded globals and calls `main()`.

## Known Bugs and Issues

These bugs exist in the current codebase. Fix them if you touch the surrounding code; otherwise leave them unless a task specifically asks for a fix.

### 1. `logger()` misconfigures `basicConfig` (`word_finder.py:17`)

```python
# WRONG — positional arg is not a valid parameter for basicConfig
lg.basicConfig(filename, level=lg.INFO, ...)

# CORRECT
lg.basicConfig(filename=filename, level=lg.INFO, ...)
```

### 2. `letters` referenced before definition in `main()` (`word_finder.py:44`)

`run_combinations` is called with `iterator=letters`, but `letters` is defined at module level (`word_finder.py:50`) only inside the `if __name__ == '__main__'` block. Calling `main()` programmatically (imported) will raise `NameError`. The function parameter `input_string` is ignored inside `main`.

**Fix:** replace `iterator=letters` with `iterator=input_string`.

### 3. SSL certificate verification disabled (`word_finder.py:21-23`)

```python
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```

This silences TLS errors and is a security risk. It was likely added to work around an expired/self-signed certificate at the Stanford URL. Prefer fixing the URL or providing a CA bundle rather than disabling verification wholesale.

### 4. `read_url` ignores its `url` parameter (`word_finder.py:24-28`)

The method signature accepts `url` but uses `self.url` internally. The parameter is dead code.

### 5. `main()` hard-codes `n=5` (`word_finder.py:43`)

```python
find_word = word_finder(url, input_string, 5, filename)   # n=5 always
```

The `n` parameter passed to `main()` is ignored.

## Development Conventions

### Style

- The existing code does not follow a consistent style guide. When adding new code, prefer PEP 8.
- Class names should be `CapWords` by convention; `word_finder` should ideally be `WordFinder`.
- Do not rename the class without updating all references and the README.

### Logging

Logging is wired up but non-functional due to bug #1 above. All `lg.info()` calls currently produce no file output. Once the bug is fixed, logs will be written to the path stored in `self.filename`.

### No Tests Exist

There is no test suite. If you add tests:
- Place them in a `tests/` directory.
- Use `pytest` as the test runner.
- Add `pytest` to a `requirements-dev.txt`.

### No Linting / Formatting Config

There is no `.flake8`, `.pylintrc`, `pyproject.toml`, or `black` configuration. If you add linting:
- Use `flake8` or `ruff` for linting.
- Use `black` for formatting.
- Add config to `pyproject.toml`.

## Common Tasks

### Change the letter set

Edit `word_finder.py:50`:
```python
letters = ['a', 'e', 'i', 'o', 'u', 'r', 's', 't']
```

### Change word length (currently always 5)

Fix bug #5 first, then change `n=5` in `word_finder.py:50-52` or pass a different `n` to `main()`.

### Add a `requirements.txt`

```
numpy>=1.20
```

### Add tests (none currently exist)

```bash
mkdir tests
# write tests/test_word_finder.py using pytest
pip install pytest
pytest tests/
```

## External Data Source

The word list is fetched from:
```
https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt
```

This is Donald Knuth's Stanford GraphBase 5-letter word list (~5,757 words). The script has no offline fallback; if this URL is unavailable, the script will fail with a network error.
