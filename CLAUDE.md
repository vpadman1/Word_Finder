# CLAUDE.md

This file provides guidance for AI assistants working in the Word_Finder repository.

## Project Overview

Word_Finder is a single-file Python utility that finds valid English words formable from a given set of letters. It works by:
1. Fetching a word list from Stanford's SGB (Stanford GraphBase) dataset over HTTPS (cached to disk after the first run)
2. Filtering the word list: keeping only words whose every character appears in the supplied letter set
3. Returning and printing the matching words

The matching rule allows letter repetition — a letter can be used more than once in a word as long as it appears in the supplied set.

## Repository Structure

```
Word_Finder/
├── CLAUDE.md           # This file
├── README.md           # Brief function-level description
├── word_finder.py      # Entire application — one file, ~65 lines
└── .word_cache.txt     # Auto-generated disk cache (gitignore candidate)
```

There are no subdirectories, no test suite, no CI configuration, and no packaging files.

## Dependencies

| Dependency      | Source | Purpose                                        |
|-----------------|--------|------------------------------------------------|
| `logging`       | stdlib | Structured log output to `word_finder.log`     |
| `ssl`           | stdlib | Custom SSL context for HTTPS fetch             |
| `urllib.request`| stdlib | Fetch word list from URL                       |
| `pathlib`       | stdlib | Cross-platform path handling for cache file    |

**No third-party dependencies.** numpy and itertools were removed during the performance rewrite.

## Running the Script

```bash
python word_finder.py
```

The entry point uses a hard-coded letter set:

```python
letters = ['q', 'w', 'y', 'i', 'p', 'd', 'f', 'h', 'j', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
main(letters=letters, n=5)
```

Change `letters` in `word_finder.py:62` to alter the input set. Change `n` to find words of a different length.

On the **first run** the script fetches the word list over the network and writes it to `.word_cache.txt`. Every subsequent run reads from the cache (no network needed).

## Code Architecture

### Constants (`word_finder.py:6-7`)

| Name            | Value                                          | Purpose                           |
|-----------------|------------------------------------------------|-----------------------------------|
| `WORD_LIST_URL` | Stanford SGB words URL                         | Default remote word list          |
| `_CACHE_FILE`   | `<script dir>/.word_cache.txt`                 | Disk cache path                   |

### Class: `WordFinder` (`word_finder.py:16`)

| Method       | Signature                     | Purpose                                          |
|--------------|-------------------------------|--------------------------------------------------|
| `__init__`   | `(url, n, use_cache)`         | Stores config; all params have sensible defaults |
| `_load_words`| `()`                          | Returns word list from cache or URL              |
| `find`       | `(letters) -> list[str]`      | Filters word list; returns matching words        |

### Function: `main` (`word_finder.py:55`)

Thin orchestrator: creates a `WordFinder`, calls `find()`, and prints results.

### Entry Point (`word_finder.py:61-63`)

Sets the letter set and calls `main()`.

## Performance

### Why the old approach was slow

The original code generated every possible `n`-length product of the letter set
with `itertools.product`, then intersected that huge list with the word list:

```
16 letters, n=5  →  16^5 = 1 048 576 strings constructed, joined, stored, sorted
```

That's over a million allocations before any matching happens.

### What the rewrite does instead

Filter the word list directly:

```
~5 757 words × 5 chars each = ~28 785 character lookups (set membership, O(1) each)
```

**Speedup: ~36× fewer operations**, plus zero extra memory for intermediate strings.

The algorithm is equivalent: a word matches if and only if every character in it
is a member of the letter set — which is exactly the set of words that would have
appeared in the `itertools.product` output.

### Disk cache

The first run fetches the ~45 KB word list over HTTPS once and writes it to
`.word_cache.txt`. Every subsequent run skips the network entirely (reads ~45 KB
from local disk). This makes re-runs nearly instant.

## SSL Note

Certificate verification is still disabled for the Stanford URL:

```python
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```

This was kept to avoid breaking the fetch against the existing URL. If the URL is
ever updated to one with a valid cert, remove these two lines and delete the
`ctx` customisation.

## Development Conventions

### Style

- Follow PEP 8 for all new code.
- Class names use `CapWords` (`WordFinder`).
- Private helpers are prefixed with `_` (`_load_words`, `_CACHE_FILE`).

### Logging

Logs are written to `word_finder.log` in the working directory. The log file is
created automatically on first run. Do not print debug output to stdout; use
`log.info()` / `log.warning()` instead.

### No Tests Exist

There is no test suite. If you add tests:
- Place them in a `tests/` directory.
- Use `pytest` as the test runner.
- Add `pytest` to a `requirements-dev.txt`.

Useful test cases:
- Letters that produce zero matches (e.g. all consonants with no vowels).
- `n` values other than 5.
- Cache hit vs. cache miss paths in `_load_words`.

### No Linting / Formatting Config

If you add linting, put config in `pyproject.toml` and use `ruff` + `black`.

## Common Tasks

### Change the letter set

Edit `word_finder.py:62`:
```python
letters = ['a', 'e', 'i', 'o', 'u', 'r', 's', 't']
```

### Find words of a different length

Pass a different `n`:
```python
main(letters=letters, n=4)   # 4-letter words
```

### Force a fresh fetch (bypass cache)

```python
finder = WordFinder(use_cache=False)
result = finder.find(letters)
```

Or simply delete `.word_cache.txt`.

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

This is Donald Knuth's Stanford GraphBase 5-letter word list (~5,757 words). The
script has no offline fallback on the first run. Once `.word_cache.txt` exists,
the script works without network access.
