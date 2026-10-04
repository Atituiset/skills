# Narration and captions

## Reuse and synthesis

Reuse valid voice clips and their word boundaries. For changed text, regenerate only changed scenes, update measured durations, and rebuild the affected timing. Do not claim an audio take is reproducible byte-for-byte; remote TTS services can change.

For Chinese, the starting voice is Edge TTS `zh-CN-XiaoxiaoNeural`, rate `+3%`, with native `WordBoundary` events. This is a default, not a restriction. The bundled script needs `edge-tts` in a Python environment and `ffmpeg` / `ffprobe` on PATH:

```bash
python3 -m venv .venv
.venv/bin/pip install edge-tts
.venv/bin/python <skill-dir>/scripts/gen-voice.py --project . --dry-run
.venv/bin/python <skill-dir>/scripts/gen-voice.py --project .
.venv/bin/python <skill-dir>/scripts/gen-voice.py --project . --only 3 7
```

`SCRIPT.md` uses headings containing `(Frame N)` and indented narration paragraphs. Example:

```markdown
## Information flow (Frame 1)

    你问了一个问题，答案为什么会一个字一个字地出现？
```

The script records a successful scene's metadata immediately. Existing clips for other scenes are preserved during partial regeneration. A failed synthesis must not silently replace a valid audio clip.

For English, the same helper supports an English Edge voice with native word boundaries. A tested starting point is `en-US-GuyNeural`, rate `+0%`; preserve a requested voice instead. Set the voice explicitly because the helper defaults to Chinese:

```bash
.venv/bin/python <skill-dir>/scripts/gen-voice.py --project <english-project> --voice en-US-GuyNeural --rate=+0%
python3 <skill-dir>/scripts/prepare-timeline.py --project <english-project> --language en
```

Kokoro with suitable alignment or another available engine is also valid. Normalize its output to the same metadata format. Translating captions alone does not produce an English video.

## Metadata contract

`audio_meta.json`:

```json
{
  "voices": [{
    "frame": 1,
    "path": "audio/voice-01.wav",
    "duration_s": 3.2,
    "text": "你问了一个问题。",
    "words": [
      {"text": "你", "start": 0.1, "end": 0.25},
      {"text": "问了", "start": 0.25, "end": 0.65},
      {"text": "一个问题", "start": 0.65, "end": 1.6}
    ]
  }]
}
```

Times are seconds relative to the clip. Duration comes from the audio file. `text` preserves source punctuation for caption recovery. Copy or generate audio under `public/` before rendering; the timeline helper copies project-relative audio there.

## Phrase captions

`prepare-timeline.py` groups consecutive words by pauses, phrase punctuation, duration and text length. It preserves their timing and emits local pages with Remotion-compatible word fields (`text`, `startMs`, `endMs`, `timestampMs`, `confidence`). Chinese uses compact pause/length grouping; English respects sentence-ending periods and splits longer sentences near clause boundaries, preserving spaces after punctuation. `--language auto` detects CJK words; select `--language en` explicitly for English narration containing occasional Chinese names. Review phrase boundaries, technical names, abbreviations and decimals: punctuation heuristics are a starting point, not a linguistic parser. Verify complete token coverage and rendered line widths in both languages.

Copy `assets/QuietCaptions.tsx` into the project and pass one scene's `captionPages`. The component shows the whole current phrase with the default quiet styling defined in `SKILL.md`. It deliberately does not recolor the active word. Word boundaries remain useful for scene cues even when captions do not highlight them.

## One visible subtitle source

Choose the delivery mode explicitly:

- **Burned-in (default):** render the single caption overlay into the video. Store optional SRT backups under `subtitles/`, separately from MP4s. This prevents player auto-loading from creating a second visible layer.
- **External:** render no caption overlay and deliver the subtitle track as requested.

During a scene overlap, the outgoing caption must expire before the incoming phrase appears. Keep helper notes and scene labels away from the narration line; a full explanatory sentence near the bottom can look like a second subtitle even without duplicated caption code.

Native word boundaries are machine timing, not proof that pronunciation sounds natural. Mixed Chinese/English terms need listening when an audio review tool or user feedback is available. State the extent of verification accurately.
