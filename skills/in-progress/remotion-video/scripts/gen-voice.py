#!/usr/bin/env python3
"""Synthesize changed scenes with a selected Edge voice and native word boundaries; checkpoint per scene."""
import argparse
import asyncio
import json
import re
import subprocess
from pathlib import Path


def parse_script(text):
    scenes, current = [], None
    for line in text.splitlines():
        heading = re.match(r'^#{2,3}\s+.*?\(Frame\s+(\d+)\)', line, re.I)
        if heading:
            if current:
                scenes.append(current)
            current = {'frame': int(heading[1]), 'text': ''}
        elif current and (line.startswith('    ') or line.startswith('\t')):
            current['text'] += (' ' if current['text'] else '') + line.strip()
    if current:
        scenes.append(current)
    if not scenes or any(not s['text'] for s in scenes):
        raise ValueError('Use headings with (Frame N) and indented narration for every scene.')
    if len({s['frame'] for s in scenes}) != len(scenes):
        raise ValueError('Duplicate Frame numbers in SCRIPT.md')
    return scenes


async def synth(text, target, voice, rate):
    import edge_tts
    words = []
    with target.open('wb') as stream:
        async for item in edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary').stream():
            if item['type'] == 'audio':
                stream.write(item['data'])
            elif item['type'] == 'WordBoundary':
                start = item['offset'] / 10_000_000
                words.append({'text': item['text'], 'start': round(start, 6),
                              'end': round(start + item['duration'] / 10_000_000, 6)})
    if not words or target.stat().st_size == 0:
        raise ValueError('TTS returned no audio or no word boundaries')
    return words


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--voice', default='zh-CN-XiaoxiaoNeural')
    parser.add_argument('--rate', default='+3%')
    parser.add_argument('--only', type=int, nargs='+')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    project = args.project.resolve()
    scenes = parse_script((project / 'SCRIPT.md').read_text())
    if args.only:
        missing = set(args.only) - {s['frame'] for s in scenes}
        if missing:
            parser.error(f'Unknown frames: {sorted(missing)}')
        scenes = [s for s in scenes if s['frame'] in args.only]
    if args.dry_run:
        print(json.dumps(scenes, ensure_ascii=False, indent=2))
        return
    meta_path = project / 'audio_meta.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {'voices': []}
    existing = {v['frame']: v for v in meta['voices']}
    out = project / 'audio'
    out.mkdir(exist_ok=True)
    for scene in scenes:
        n = scene['frame']
        mp3, wav = out / f'voice-{n:02d}.mp3', out / f'voice-{n:02d}.wav'
        temp_mp3, temp_wav = out / f'.voice-{n:02d}.tmp.mp3', out / f'.voice-{n:02d}.tmp.wav'
        try:
            words = asyncio.run(synth(scene['text'], temp_mp3, args.voice, args.rate))
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(temp_mp3), '-ar', '44100', '-ac', '1', str(temp_wav)], check=True)
            duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(temp_wav)], text=True))
            temp_mp3.replace(mp3)
            temp_wav.replace(wav)
            existing[n] = {**scene, 'path': f'audio/{wav.name}', 'duration_s': duration,
                           'voice': args.voice, 'rate': args.rate, 'words': words}
            meta['voices'] = [existing[k] for k in sorted(existing)]
            pending = meta_path.with_suffix('.tmp.json')
            pending.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
            pending.replace(meta_path)
            print(f'Frame {n}: {duration:.3f}s, {len(words)} words', flush=True)
        finally:
            temp_mp3.unlink(missing_ok=True)
            temp_wav.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
