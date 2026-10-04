#!/usr/bin/env python3
"""Check a rendered file against generated timing; does not replace visual/audio review."""
import argparse
import json
import subprocess
from fractions import Fraction
from pathlib import Path


def verify(project, video, width, height, caption_mode):
    timeline = json.loads((project / 'src/generated/timeline.json').read_text())
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)], text=True))
    streams = probe['streams']
    picture = next((s for s in streams if s['codec_type'] == 'video'), None)
    audio = next((s for s in streams if s['codec_type'] == 'audio'), None)
    errors = []
    if picture is None:
        raise ValueError('No video stream')
    if picture['width'] != width or picture['height'] != height:
        errors.append('Dimensions differ from requested output')
    fps = float(Fraction(picture['avg_frame_rate']))
    if abs(fps - timeline['fps']) > .001:
        errors.append('Frame rate differs from timeline')
    frames = picture.get('nb_frames')
    if frames not in (None, 'N/A') and int(frames) != timeline['totalFrames']:
        errors.append('Frame count differs from timeline')
    if abs(float(probe['format']['duration']) - timeline['totalFrames'] / timeline['fps']) > max(.12, 2 / timeline['fps']):
        errors.append('Duration differs from timeline')
    if timeline['scenes'] and audio is None:
        errors.append('Narrated timeline has no audio stream')
    if caption_mode == 'burned':
        if any(s['codec_type'] == 'subtitle' for s in streams):
            errors.append('Burned captions plus embedded subtitle stream may duplicate subtitles')
        for ext in ('.srt', '.ass', '.vtt', '.ssa'):
            if video.with_suffix(ext).exists():
                errors.append(f'Auto-loadable sidecar {video.with_suffix(ext).name}; move optional subtitles to subtitles/')
    if errors:
        raise ValueError('; '.join(errors))
    return {'video': str(video), 'width': width, 'height': height, 'fps': fps,
            'duration': float(probe['format']['duration']), 'frames': frames,
            'audioCodec': audio['codec_name'] if audio else None,
            'captionMode': caption_mode, 'visualReview': 'not assessed by this script'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--video', type=Path, required=True)
    p.add_argument('--width', type=int, default=1920)
    p.add_argument('--height', type=int, default=1080)
    p.add_argument('--caption-mode', choices=['burned', 'external'], default='burned')
    a = p.parse_args()
    root = a.project.resolve()
    video = a.video if a.video.is_absolute() else root / a.video
    print(json.dumps(verify(root, video, a.width, a.height, a.caption_mode), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
