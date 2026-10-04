#!/usr/bin/env python3
"""Pre-render hygiene gate for a HyperFrames project.

A scan costs seconds; discovering its finding in the output costs a delivery
render. Run this before every render, and fold it into the project's own
`verify` step so nobody has to remember.

    python3 scripts/check-hygiene.py <project-dir>

Two gates:

  motion    authored `will-change`, CSS `transition`/`animation`, `@keyframes`
            hard-fail; a tweened `filter` warns with its duration, because the
            judder boundary is the hold rather than the tween.
  deps      any `<script src>` / `<link href>` pointing at a remote origin
            hard-fails. A CDN animation library fails the render *after* every
            frame is captured, so a transient network blip costs the whole run.

Exit codes:
    0  clean, or warnings only
    1  a hard failure
    2  bad usage

Why the false-positive filters matter: tldraw's exported SVGs inline a full
computed-style dump (`tl-export-embed-styles`) on every foreignObject child.
That dump contains ~300 literal `will-change: auto` per project, plus inert
`transition`/`animation`/`filter` defaults. A raw grep reports the project as
contaminated and gets ignored, which is worse than not scanning at all. Every
rule below filters those out before deciding anything.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# --- dependency rules -----------------------------------------------------
# A remote <script src> / <link href>. The animation library is the one that
# bites: loaded from a CDN once per composition, one render issues dozens of
# concurrent requests for the same file, and the run dies at the VALIDATION
# step — after every frame is already captured. A transient network blip then
# costs the whole delivery render.
RE_REMOTE_SRC = re.compile(
    r"""<(?:script\b[^>]*\bsrc|link\b[^>]*\bhref)\s*=\s*["']\s*(https?:)?//""",
    re.I,
)

# --- motion rules ---------------------------------------------------------

# `will-change` is only authored if its value is not the initial `auto`.
# tldraw always emits `auto`; anything else was typed by a human.
RE_WILL_CHANGE = re.compile(r"will-change\s*:\s*([a-zA-Z-]+)")
RE_WILL_CHANGE_AUTHORED = re.compile(
    r"will-change\s*:\s*(?!auto\b)(transform|opacity|filter|contents|[a-zA-Z-]+)"
)
RE_WILL_CHANGE_CSS = re.compile(r"will-change\s*:\s*(?!auto\b)[a-zA-Z-]+")

# Authored CSS lives in <style> blocks. Inline style="" attributes on tldraw
# nodes are the dumps and are excluded by construction.
RE_STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)

RE_CSS_TRANSITION = re.compile(r"(?<![\w-])transition\s*:(?!none\b|all 0s|)[^;}]+", re.I)
RE_CSS_ANIMATION = re.compile(r"(?<![\w-])animation\s*:(?!none\b)[^;}]+", re.I)
RE_KEYFRAMES = re.compile(r"@(?:-webkit-)?keyframes", re.I)

# A tween that touches `filter` at all. Duration is captured so the report can
# distinguish a short entry reveal from a filter left alive across a hold.
RE_TWEEN_CALL = re.compile(r"\.(to|fromTo|set)\s*\(", re.I)
RE_FILTER_PROP = re.compile(r"(?<![\w-])filter\s*:")
RE_DURATION = re.compile(r"duration\s*:\s*([0-9.]+)")

HOLD_SECONDS = 1.0  # a filter tween longer than this likely spans a hold


def balanced_body(text: str, open_paren: int) -> str:
    """Return the text between the paren at `open_paren` and its match.

    A fixed-size lookahead window is wrong here: it bleeds into the *next*
    statement and reports a filter tween that does not exist, which teaches the
    reader to ignore the scan. Parse the call's own arguments instead.
    """
    depth = 0
    for i in range(open_paren, min(open_paren + 2000, len(text))):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren + 1 : i]
    return text[open_paren : open_paren + 400]

# --- collection ------------------------------------------------------------


def authored_css_blocks(text: str) -> list[tuple[int, str]]:
    """Yield (offset, css) for every <style> block."""
    return [(m.start(), m.group(1)) for m in RE_STYLE_BLOCK.finditer(text)]


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


_RE_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_RE_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_RE_LINE_COMMENT = re.compile(r"(?<![:'\"])//[^\n]*")


def blank_comments(text: str) -> str:
    """Replace comment bodies with spaces, preserving every offset.

    A scan must read **code**, not text. Comments in this project routinely name
    the very things being scanned — a composition's determinism contract says
    "no CSS transition and no @keyframes", which a naive grep reports as two
    violations. Blanking rather than deleting keeps line numbers and positions
    valid, so findings still point at the right line.
    """
    def blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))
    out = _RE_HTML_COMMENT.sub(blank, text)
    out = _RE_BLOCK_COMMENT.sub(blank, out)
    out = _RE_LINE_COMMENT.sub(blank, out)
    return out


def scan_file(path: Path) -> tuple[list[str], list[str]]:
    """Return (failures, warnings) for one file."""
    failures: list[str] = []
    warnings: list[str] = []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:  # pragma: no cover
        return [f"{path}: cannot read ({exc})"], []

    rel = path.name
    # Scan code, not prose: comments name the banned constructs by name.
    code = blank_comments(text)

    # 0. remote dependency — a CDN script fails the render after every frame
    #    is captured, so a network blip costs the whole run.
    for m in RE_REMOTE_SRC.finditer(code):
        failures.append(
            f"{rel}:{line_of(text, m.start())}  remote {m.group(1)}: "
            f"{m.group(2)[:60]} — vendor it into assets/vendor/ and point at the "
            "root-relative path the fonts already use"
        )

    # 1. authored will-change — anywhere, since inline style attrs only ever
    #    carry the inert `auto` value from tldraw.
    for m in RE_WILL_CHANGE_AUTHORED.finditer(code):
        failures.append(
            f"{rel}:{line_of(text, m.start())}  will-change: {m.group(1)} — "
            "this pipeline carries no will-change; GSAP tweens the properties directly"
        )

    # 2. authored CSS transition / animation / keyframes — <style> blocks only.
    for offset, css in authored_css_blocks(code):
        base = offset
        for pat, label in (
            (RE_CSS_TRANSITION, "transition"),
            (RE_CSS_ANIMATION, "animation"),
        ):
            for m in pat.finditer(css):
                # `transition:21-codex-workbuddy:22-final-map:crossfade` is a
                # data-attribute *value* caught by a loose match; a real CSS
                # declaration ends with a length/keyword, not a bare token
                # containing '-'. Require the value to look like CSS.
                val = m.group(0).split(":", 1)[1].strip()
                if val.startswith(tuple("0123456789")) or any(
                    kw in val for kw in ("s ", "ms", "ease", "cubic", "linear", "steps")
                ):
                    failures.append(
                        f"{rel}:{line_of(text, base + m.start())}  CSS {label}: {val[:60]} — "
                        "authored CSS animation fights per-frame-seek determinism"
                    )
        for m in RE_KEYFRAMES.finditer(css):
            failures.append(
                f"{rel}:{line_of(text, base + m.start())}  @keyframes — "
                "a wall-clock animation a seek cannot reproduce deterministically"
            )

    # 3. tweened filter — a warning, because a short entry reveal is legal and
    #    only a hold-crossing filter judders. Parse the call's own arguments so
    #    a neighbouring statement's filter is never attributed to this one.
    for m in RE_TWEEN_CALL.finditer(code):
        kind = m.group(1).lower()
        body = balanced_body(text, text.index("(", m.start()))
        if not RE_FILTER_PROP.search(body):
            continue
        # `.set()` is a discrete assignment at one instant, not a per-frame
        # animation: it cannot judder, so it is not reported.
        if kind == "set":
            continue
        dur = RE_DURATION.search(body)
        d = float(dur.group(1)) if dur else None
        note = (
            f"filter tweened, duration={d}s — if this filter stays live across "
            "a hold it is judder; a sub-second entry reveal is fine"
        )
        if d is not None and d > HOLD_SECONDS:
            warnings.append(f"{rel}:{line_of(text, m.start())}  {note} [LONG]")
        else:
            warnings.append(f"{rel}:{line_of(text, m.start())}  {note}")

    return failures, warnings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2

    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    targets = sorted(
        {p.resolve() for p in [root / "index.html", root / "index-episodes.html"]}
        | set((root / "compositions").rglob("*.html"))
        | set(root.glob("*.html"))
    )
    # Build scratch is not authored source: `.hf-work/` holds scratch hosts and
    # `work-*` holds a render's intermediates. Scanning them reports findings in
    # files nobody maintains.
    def authored(t: Path) -> bool:
        parts = t.relative_to(root).parts
        return t.is_file() and not any(
            p.startswith(".") or p.startswith("work-") for p in parts[:-1]
        )
    targets = [t for t in targets if authored(t)]
    if not targets:
        print(f"no HTML found under {root}", file=sys.stderr)
        return 2

    failures: list[str] = []
    warnings: list[str] = []
    for t in targets:
        f, w = scan_file(t)
        failures += f
        warnings += w

    print(f"motion hygiene: {len(targets)} file(s) under {root}")

    if warnings:
        print(f"\n  {len(warnings)} warning(s) — review each against the hold boundary:")
        for w in warnings:
            print(f"    ! {w}")

    if failures:
        print(f"\n  {len(failures)} FAILURE(S):")
        for f in failures:
            print(f"    x {f}")
        print("\n  Fix these before rendering. Each one is a judder or a")
        print("  determinism regression that costs a full render to discover.")
        return 1

    print("\n  clean: no authored will-change, no CSS animation, no @keyframes.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))