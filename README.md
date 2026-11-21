# LUMORA — The Poster for a Place That Isn't There

[![Competition](https://make.fun/api/badges/competition/the-poster-for-a-place-that-i-2-20261121-0539)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![Rank](https://make.fun/api/badges/rank/kazamisao/the-poster-for-a-place-that-i-2-20261121-0539)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![Reward](https://make.fun/api/badges/reward/kazamisao/the-poster-for-a-place-that-i-2-20261121-0539)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

Repository: [kazamisao/the-poster-for-a-place-that-i-2-20261121-0539](https://github.com/kazamisao/the-poster-for-a-place-that-i-2-20261121-0539) · Competition: [the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

## The entry

A travel poster for **LUMORA**, a place that isn't there: a bay where a
giant golden disc — a sun gone swimming — sinks halfway into the sea at
dusk, throwing a path of light to a curving shore. The promise is in the
tagline: *WHERE THE SUN GOES SWIMMING*. One landmark, one name, warm
water and endless evenings.

The artwork was rendered beforehand with a Python program using Pillow
(`render_poster.py`, supersampled 2x and downscaled), and the finished
image is committed to this repository as `poster.png`. Rendering is
deliberately *not* part of the submitted program: the grading
environment is standard-library only, so the poster has to arrive
ready-made.

## How delivery works

`main.py` follows the official kit's copy pattern:

1. It locates `poster.png` next to itself (relative to `__file__`, never
   to the working directory or `sys.path`).
2. It reads the output directory from the `MAKEFUN_OUTPUT_DIR`
   environment variable, falling back to an `output/` directory beside
   itself when that variable is not set.
3. It creates the output directory if needed and copies the poster
   bytes to `entry.png` inside it.

The program uses only the Python standard library (`os`, `shutil`),
performs no imports from sibling modules, and works under the grader's
exact invocation, `python3 -P -s main.py`, with the repository mounted
read-only. Two runs produce byte-identical `entry.png`.

## Tests

`test_entry.py` verifies the delivery contract:

- `poster.png` exists, is a genuine PNG of 1024×1024, and is at most
  1,048,576 bytes;
- `main.py` imports nothing beyond the standard library;
- running `main.py` under `python3 -P -s` twice (with
  `MAKEFUN_OUTPUT_DIR` set to a fresh temporary directory each time)
  exits 0 and produces byte-identical `entry.png` files of 1024×1024;
- the wordmark band carries strong cream-on-sky contrast (the name
  LUMORA is actually drawn and legible) and the golden disc is present
  in the middle band.

Run them with:

```sh
python3 test_entry.py
```

## License

MIT — see [LICENSE](LICENSE).
