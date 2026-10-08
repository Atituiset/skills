#!/usr/bin/env python3
"""Per-line edge-tts with word boundaries -> audio/voice-NN.wav + audio_meta.json (product-launch shape).

Usage: python gen-voice.py [--project <dir>] [frame numbers to (re)generate; default: all]
Requires: edge-tts in the running python (use a project venv)."""
import asyncio, json, re, subprocess, sys
from pathlib import Path

import edge_tts

# project root: --project <dir> or cwd
_argv = sys.argv[1:]
ROOT = Path.cwd()
if "--project" in _argv:
    _i = _argv.index("--project")
    ROOT = Path(_argv[_i + 1]).resolve()
    del _argv[_i:_i + 2]
sys.argv = [sys.argv[0]] + _argv
SCRIPT = ROOT / "SCRIPT.md"
OUT = ROOT / "audio"
# The voice and rate come from the script's OWN front matter, not from here:
#   voice: edge-tts zh-CN-XiaoxiaoNeural rate +3%
# A hard-coded voice is how an English project ends up narrated in Chinese, or an English
# line read at a Chinese-tuned rate. The front matter is the one place a project states
# what it is.
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+3%"
try:
    _fm = re.search(r"^voice:\s*edge-tts\s+(\S+)\s+rate\s*(\S+)\s*$",
                    (ROOT / "SCRIPT.md").read_text(encoding="utf-8"), re.M)
    if _fm:
        VOICE, RATE = _fm.group(1), _fm.group(2)
except FileNotFoundError:
    pass

def parse_script(md: str):
    lines, cur = [], None
    for raw in md.splitlines():
        h = re.match(r"^#{2,3}\s+.*?\(frame\s+(\d+)\)", raw, re.I)
        if h:
            if cur and cur["text"].strip():
                lines.append(cur)
            cur = {"frame": int(h.group(1)), "text": ""}
            continue
        if cur is None or raw.strip().startswith("**"):
            continue
        m = re.match(r"^(?: {4,}|\t)(.+)$", raw)
        if m:
            cur["text"] += (" " if cur["text"] else "") + m.group(1).strip()
    if cur and cur["text"].strip():
        lines.append(cur)
    return lines

async def synth(text: str, mp3: Path):
    words = []
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                off = chunk["offset"] / 10_000_000  # 100ns ticks -> s
                dur = chunk["duration"] / 10_000_000
                words.append({"text": chunk["text"], "start": round(off, 3), "end": round(off + dur, 3)})
    return words

def main():
    only = {int(x) for x in sys.argv[1:]}  # e.g. `gen-voice.py 3 4 5` regenerates just those lines
    OUT.mkdir(exist_ok=True)
    lines = parse_script(SCRIPT.read_text(encoding="utf-8"))
    if only:
        meta = json.loads((ROOT / "audio_meta.json").read_text(encoding="utf-8"))
        by_frame = {v["frame"]: v for v in meta["voices"]}
        voices = []
        for ln in lines:
            if ln["frame"] not in only:
                continue
            n = ln["frame"]
            mp3 = OUT / f"voice-{n:02d}.mp3"
            wav = OUT / f"voice-{n:02d}.wav"
            words = asyncio.run(synth(ln["text"], mp3))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3),
                            "-ar", "44100", "-ac", "1", str(wav)], check=True)
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                        "-of", "csv=p=0", str(wav)], capture_output=True, text=True, check=True).stdout.strip())
            for i, w in enumerate(words):
                w["id"] = f"w{i}"
            by_frame[n] = {"frame": n, "path": f"audio/voice-{n:02d}.wav",
                           "duration_s": round(dur, 3), "words": words}
            print(f"✓ frame {n:02d}: {dur:.2f}s, {len(words)} words — {ln['text'][:24]}…")
        meta["voices"] = [by_frame[k] for k in sorted(by_frame)]
        (ROOT / "audio_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        total = sum(v["duration_s"] for v in meta["voices"])
        print(f"\n✓ audio_meta.json merged — {len(meta['voices'])} lines, narration total {total:.1f}s")
        return
    lines = parse_script(SCRIPT.read_text(encoding="utf-8"))
    voices = []
    for ln in lines:
        n = ln["frame"]
        mp3 = OUT / f"voice-{n:02d}.mp3"
        wav = OUT / f"voice-{n:02d}.wav"
        words = asyncio.run(synth(ln["text"], mp3))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3),
                        "-ar", "44100", "-ac", "1", str(wav)], check=True)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                    "-of", "csv=p=0", str(wav)], capture_output=True, text=True, check=True).stdout.strip())
        for i, w in enumerate(words):
            w["id"] = f"w{i}"
        voices.append({"frame": n, "path": f"audio/voice-{n:02d}.wav",
                       "duration_s": round(dur, 3), "words": words})
        print(f"✓ frame {n:02d}: {dur:.2f}s, {len(words)} words — {ln['text'][:24]}…")
    meta = {"bgm": None, "bgm_pending": False, "voices": voices, "sfx": []}
    (ROOT / "audio_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(v["duration_s"] for v in voices)
    print(f"\n✓ audio_meta.json — {len(voices)} lines, narration total {total:.1f}s")

if __name__ == "__main__":
    main()
