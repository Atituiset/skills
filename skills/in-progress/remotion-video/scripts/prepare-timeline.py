#!/usr/bin/env python3
"""Build measured scene timing, quiet phrase captions, and a separate SRT backup."""
import argparse
import json
import math
import re
import shutil
from pathlib import Path

PUNCT = re.compile(r'^[，。！？；：、—…,.!?;:]+')


def text_words(words, script):
    source, cursor, result = re.sub(r'\s', '', script), 0, []
    for item in words:
        word = dict(item)
        plain = re.sub(r'\s', '', word['text'])
        at = source.find(plain, cursor) if source else -1
        if at >= 0:
            cursor = at + len(plain)
            mark = PUNCT.match(source[cursor:])
            if mark and not PUNCT.search(word['text'][-1:]):
                word['text'] += mark[0]
                cursor += len(mark[0])
        if result and re.search(r'[A-Za-z0-9][,.;:!?]*$', result[-1]['text']) and re.match(r'[A-Za-z0-9]', word['text']):
            word['text'] = ' ' + word['text']
        result.append(word)
    return result


def make_pages(words, script, language='auto'):
    cjk = language == 'zh' or (language == 'auto' and any(
        re.search(r'[\u3400-\u9fff]', w['text']) for w in words))
    display_words = text_words(words, script)
    groups, current = [], []
    if cjk:
        limit = 29
        for word in display_words:
            count = sum(len(w['text']) for w in current)
            if current and ((count >= 9 and word['start'] - current[-1]['end'] >= .28)
                            or count + len(word['text']) > limit
                            or word['end'] - current[0]['start'] > 5.8
                            or re.search(r'[。！？!?]$', current[-1]['text'])):
                groups.append(current)
                current = []
            current.append(word)
        if current:
            groups.append(current)
    else:
        sentences, current = [], []
        for word in display_words:
            current.append(word)
            if re.search(r'[.!?]$', word['text']):
                sentences.append(current)
                current = []
        if current:
            sentences.append(current)
        groups = []
        def split_phrase(items):
            length = sum(len(w['text']) for w in items)
            if length <= 82 and items[-1]['end'] - items[0]['start'] <= 6:
                groups.append(items)
                return
            candidates = []
            for i in range(3, len(items)-2):
                left = sum(len(w['text']) for w in items[:i])
                if left < 22:
                    continue
                quality = abs(left - length / 2)
                if re.search(r'[,;:]$', items[i-1]['text']):
                    quality -= 22
                elif items[i]['text'].strip().lower() in ('and','but','which','while','so','then','to','from','with'):
                    quality -= 10
                candidates.append((quality, i))
            if not candidates:
                groups.append(items)
                return
            _, cut = min(candidates)
            split_phrase(items[:cut])
            split_phrase(items[cut:])
        for sentence in sentences:
            split_phrase(sentence)
    pages = []
    for group in groups:
        items = [{'text': w['text'], 'startMs': round(w['start'] * 1000),
                  'endMs': round(w['end'] * 1000), 'timestampMs': None, 'confidence': None} for w in group]
        pages.append({'startMs': items[0]['startMs'], 'endMs': items[-1]['endMs'] + 150,
                      'text': ''.join(w['text'] for w in items).strip(), 'words': items})
    for a, b in zip(pages, pages[1:]):
        a['endMs'] = min(a['endMs'], b['startMs'])
    return pages


def stamp(ms):
    ms = round(ms)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'


def build(project, fps, hold, language='auto'):
    meta = json.loads((project / 'audio_meta.json').read_text())
    voices = sorted(meta['voices'], key=lambda v: v['frame'])
    if not voices or len({v['frame'] for v in voices}) != len(voices):
        raise ValueError('Expected nonempty voices with unique frame IDs')
    scenes, captions, start = [], [], 0
    for v in voices:
        duration = float(v['duration_s'])
        if not math.isfinite(duration) or duration <= 0 or not v.get('words'):
            raise ValueError(f'Invalid duration or missing word timing in frame {v["frame"]}')
        previous = -1.0
        for w in v['words']:
            a, b = float(w['start']), float(w['end'])
            if not w['text'].strip() or not (math.isfinite(a) and math.isfinite(b) and 0 <= a <= b <= duration + .1 and a >= previous):
                raise ValueError(f'Invalid word timing in frame {v["frame"]}: {w}')
            previous = a
        rel = Path(v['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('Audio paths must be project-relative without ..')
        source = project / rel
        if not source.is_file():
            raise FileNotFoundError(source)
        public_rel = Path(*rel.parts[1:]) if rel.parts[0] == 'public' else rel
        target = project / 'public' / public_rel
        if source.resolve() != target.resolve():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        frames = math.ceil(duration * fps) + math.ceil(hold * fps)
        pages = make_pages(v['words'], v.get('text', ''), language)
        if pages:
            pages[-1]['endMs'] = min(pages[-1]['endMs'], round(frames / fps * 1000))
        scenes.append({'id': v['frame'], 'from': start, 'durationInFrames': frames,
                       'audio': public_rel.as_posix(), 'captionPages': pages})
        for page in pages:
            offset = start / fps * 1000
            captions.append(f'{len(captions)+1}\n{stamp(offset+page["startMs"])} --> {stamp(offset+page["endMs"])}\n{page["text"]}\n')
        start += frames
    out = project / 'src/generated'
    out.mkdir(parents=True, exist_ok=True)
    result = {'fps': fps, 'totalFrames': start, 'scenes': scenes}
    (out / 'timeline.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    subs = project / 'subtitles'
    subs.mkdir(exist_ok=True)
    (subs / 'narration.srt').write_text('\n'.join(captions))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--language', choices=('auto', 'zh', 'en'), default='auto')
    p.add_argument('--fps', type=float, default=30)
    p.add_argument('--hold', type=float, default=.8)
    a = p.parse_args()
    if not math.isfinite(a.fps) or a.fps <= 0 or not math.isfinite(a.hold) or a.hold < 0:
        p.error('fps must be positive and hold must be nonnegative')
    data = build(a.project.resolve(), a.fps, a.hold, a.language)
    print(f'{len(data["scenes"])} scenes; {data["totalFrames"]} frames; {data["totalFrames"]/a.fps:.3f}s')


if __name__ == '__main__':
    main()
