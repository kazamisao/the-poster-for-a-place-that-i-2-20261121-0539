"""Entry program for the-poster-for-a-place-that-i-2-20261121-0539.

Stdlib-only: copies the pre-rendered poster.png (committed in this
repository) to $MAKEFUN_OUTPUT_DIR/entry.png. The grader runs
`python3 -P -s` with no network and no third-party packages, so this
file imports nothing beyond the standard library and writes no other
file.
"""
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(here, "output")
    poster = os.path.join(here, "poster.png")
    if not os.path.exists(poster):
        raise SystemExit("error: poster.png missing next to main.py")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(poster, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
