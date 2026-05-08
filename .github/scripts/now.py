#!/usr/bin/env python3
"""
now.py — the profile README updater.

regenerates the entire dashboard between a single NOW:START/NOW:END marker
pair on each run. one outer code fence renders all four blocks (clock,
weather, moon, i ching) with a single copy button — much cleaner than the
per-block fence approach.

each block has its own try/except so a single failure (e.g. wttr.in
outage) renders a small placeholder for that block while the others
update normally. the readme is never partially-broken.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# local modules
sys.path.insert(0, str(Path(__file__).parent))
import iching
import moon

# --------------------------------------------------------------------------- #
# configuration
# --------------------------------------------------------------------------- #

TIMEZONE = "Europe/Lisbon"
WEATHER_CITY = "Lisbon"
COAST_PHRASE = "somewhere along the coast"

ROOT = Path(__file__).resolve().parents[2]
README_PATH = ROOT / "README.md"

USER_AGENT = "0xHalo22-profile-bot (github.com/0xHalo22/0xHalo22)"

# wttr.in narrow ASCII format. flags:
#   0 = current conditions only (no forecast)
#   n = narrow output (~29 chars wide max)
#   T = no ANSI escape codes (clean for markdown)
#   Q = no city header / no location echo
# this gives us the iconic wttr.in ASCII weather panel without the wider
# default formatting that would force a horizontal scrollbar.
WTTR_URL = f"https://wttr.in/{WEATHER_CITY}?0nTQ"

START_MARKER = "<!-- NOW:START -->"
END_MARKER = "<!-- NOW:END -->"

# --------------------------------------------------------------------------- #
# block: clock
# --------------------------------------------------------------------------- #

def local_time_string() -> str:
    """returns a 12-hour formatted local time like '12:49 AM'."""
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    hour = now.hour % 12 or 12
    minute = now.minute
    ampm = "AM" if now.hour < 12 else "PM"
    return f"{hour}:{minute:02d} {ampm}"


# --------------------------------------------------------------------------- #
# block: weather
# --------------------------------------------------------------------------- #

def fetch_weather_ascii(attempts: int = 3, base_backoff: float = 2.0) -> str:
    last_err: Exception | None = None
    backoff = base_backoff
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(WTTR_URL, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = e
            if attempt < attempts:
                print(f"    wttr.in attempt {attempt}/{attempts} failed: {e}; retrying in {backoff:.1f}s")
                time.sleep(backoff)
                backoff *= 2
    assert last_err is not None
    raise last_err


def normalize_weather(raw: str) -> str:
    """clean up wttr.in's ASCII output. it already has its own internal
    indentation that aligns the art with the side text, so we don't add any
    further indent — we just strip ANSI codes (in case T didn't catch them
    all), trim trailing whitespace per line, and drop empty bookend lines."""
    ansi = re.compile(r"\x1b\[[0-9;]*[mK]")
    raw = ansi.sub("", raw)
    lines = [ln.rstrip() for ln in raw.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def now_block() -> str:
    """time + place + wttr.in's ASCII weather panel.

    the ASCII art is what gives this cell its character — the cloud-and-sun
    drawing renders beautifully in monospace and is genuinely the soul of
    the dashboard. the panel is 5 lines, ~29 chars wide max, so the cell
    stays under 30 chars and the bar fits without horizontal scroll."""
    time_str = local_time_string()
    weather_art = normalize_weather(fetch_weather_ascii())
    return (
        f"   · {time_str}\n"
        f"   {COAST_PHRASE}\n"
        f"\n"
        f"{weather_art}"
    )


# --------------------------------------------------------------------------- #
# block: moon, iching (delegated to local modules)
# --------------------------------------------------------------------------- #

def moon_block() -> str:
    return moon.render()


def iching_block() -> str:
    """wrap the reading at ~25 chars so long aphorisms don't blow the cell
    width out and trigger a horizontal scrollbar on the readme."""
    tz = ZoneInfo(TIMEZONE)
    today = datetime.now(tz).date()
    h = iching.hexagram_for(today)
    char = iching.hexagram_char(h)
    (upper_glyph, upper_name), (lower_glyph, lower_name) = iching.trigrams_of(h)

    title = f"   {char}  {h.number} {h.pinyin} — {h.english}"
    trigrams = f"   {upper_glyph} {upper_name} over {lower_glyph} {lower_name}"
    wrapped = textwrap.fill(
        f'"{h.reading}"',
        width=28,
        initial_indent="   ",
        subsequent_indent="    ",  # one extra space so wrapped lines align under the opening quote
    )
    return f"{title}\n{trigrams}\n{wrapped}"


# --------------------------------------------------------------------------- #
# render full dashboard
# --------------------------------------------------------------------------- #

# ordered (name, generator, fallback) tuples. fallback shown if generator raises.
# three cells: time+weather merged, moon, i ching. wider cells, no scroll.
BLOCKS: list[tuple[str, callable, str]] = [
    ("now",    now_block,    f"   · {COAST_PHRASE}\n   (weather unavailable)"),
    ("moon",   moon_block,   "   🌑  (moon unavailable)"),
    ("iching", iching_block, "   ䷀  (i ching unavailable)"),
]

TOTAL_WIDTH = 104    # target total width — wide enough to spread the columns, narrow enough that the copy button doesn't clip the right edge
MIN_GAP = 3          # minimum spaces between columns (used if content is already wide)


def visual_width(line: str) -> int:
    """approximate display width of a string for column padding.

    most chars count as 1, but unicode emoji and CJK characters typically
    render about twice as wide in monospace fonts. we add 1 to those code
    points so column padding accounts for them. this isn't perfect but it's
    close enough — github's monospace rendering is somewhat font-dependent
    anyway."""
    extra = 0
    for ch in line:
        cp = ord(ch)
        # CJK unified ideographs, hexagram symbols, common emoji ranges
        if (
            0x1F300 <= cp <= 0x1FAFF       # most emoji
            or 0x2600 <= cp <= 0x27BF       # misc symbols / dingbats
            or 0x4DC0 <= cp <= 0x4DFF       # i ching hexagrams
            or 0x4E00 <= cp <= 0x9FFF       # CJK ideographs
        ):
            extra += 1
    return len(line) + extra


def pad_line(line: str, width: int) -> str:
    """right-pad with spaces until visual_width hits target."""
    diff = width - visual_width(line)
    return line + (" " * max(diff, 0))


def stitch_columns(blocks: list[str]) -> str:
    """take N block strings and stitch them into a single multi-column layout.

    each column gets its natural content width (no wasted internal padding),
    and the leftover horizontal space up to TOTAL_WIDTH is distributed evenly
    as gaps between columns. result: column 1 sits flush left, column N sits
    flush right, and intermediate columns float at even intervals — visually
    aligned with the full-width contribution graph below the dashboard."""
    grid = [b.splitlines() for b in blocks]
    height = max(len(rows) for rows in grid)
    for rows in grid:
        while len(rows) < height:
            rows.append("")

    col_widths = [
        max((visual_width(ln) for ln in rows), default=0) for rows in grid
    ]
    n = len(grid)
    leftover = TOTAL_WIDTH - sum(col_widths)
    gap_size = max(leftover // (n - 1), MIN_GAP) if n > 1 else 0
    gap = " " * gap_size

    lines: list[str] = []
    for row_idx in range(height):
        cells = [pad_line(rows[row_idx], col_widths[i]) for i, rows in enumerate(grid)]
        lines.append(gap.join(cells).rstrip())
    return "\n".join(lines)


def render_dashboard() -> tuple[str, dict[str, str]]:
    """returns (fenced_code_block, per_block_status).

    we render the dashboard as a SINGLE fenced code block containing a
    multi-column ASCII layout. this is robust against github's markdown
    quirks (unlike <pre> inside <table> cells, where backslashes and
    underscores get inconsistently mangled). one copy button as the cost
    of admission, but every character in the weather art is preserved."""
    statuses: dict[str, str] = {}
    rendered: list[str] = []
    for name, generator, fallback in BLOCKS:
        try:
            rendered.append(generator())
            statuses[name] = "ok"
        except Exception as e:
            rendered.append(fallback)
            statuses[name] = f"failed — {type(e).__name__}: {e}"
    body = stitch_columns(rendered)
    return f"```\n{body}\n```", statuses


# --------------------------------------------------------------------------- #
# readme update
# --------------------------------------------------------------------------- #

def update_readme() -> tuple[bool, dict[str, str]]:
    if not README_PATH.exists():
        raise SystemExit(f"readme not found at {README_PATH}")

    original = README_PATH.read_text(encoding="utf-8")
    if START_MARKER not in original or END_MARKER not in original:
        raise SystemExit(
            f"readme is missing the {START_MARKER} / {END_MARKER} marker pair"
        )

    body, statuses = render_dashboard()
    # body is a fenced code block — wrap it with the markers + blank lines
    block = f"{START_MARKER}\n\n{body}\n\n{END_MARKER}"

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    new_text = pattern.sub(block, original, count=1)

    if new_text == original:
        return False, statuses

    README_PATH.write_text(new_text, encoding="utf-8")
    return True, statuses


# --------------------------------------------------------------------------- #
# git commit (only when running in CI)
# --------------------------------------------------------------------------- #

def run_git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, cwd=ROOT)


def commit_if_changed() -> None:
    if not os.environ.get("GITHUB_ACTIONS"):
        return
    run_git("add", "README.md")
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if not status.stdout.strip():
        print("[now] no changes to commit")
        return
    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    msg = f"now: {stamp}"
    run_git("commit", "-m", msg)
    print(f"[now] committed: {msg}")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main() -> int:
    print("[now] regenerating profile readme")
    changed, statuses = update_readme()
    print()
    print("[now] block status:")
    for name, status in statuses.items():
        print(f"  {name:8s} → {status}")
    print()
    print(f"[now] readme changed: {changed}")
    commit_if_changed()
    return 0


if __name__ == "__main__":
    sys.exit(main())
