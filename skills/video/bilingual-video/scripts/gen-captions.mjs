#!/usr/bin/env node
/**
 * Build caption pages per SCENE from the master's own narration text + edge-tts word
 * boundaries.
 *
 * The grouping rule is the master's, ported unchanged, because it is the part that is easy to
 * get wrong in a way nobody notices until playback:
 *
 *   · Cut ONLY at punctuation, and let a long clause wrap to two rows. A first pass cut at a
 *     character count and produced 「人正在跟模型聊天每个人大约每三十」 — a caption that starts
 *     mid-phrase is the rushed-slideshow failure.
 *   · The punctuation is NOT in edge-tts's word list. `WordBoundary` returns bare word units, so
 *     a naive `word[-1] in PUNCT` never fires and every line collapses into one caption that
 *     covers the whole scene. The pauses are recovered by walking the narration text and the
 *     word list side by side.
 *
 * Times are emitted SCENE-LOCAL: each scene plays inside its own Sequence, so `useCurrentFrame()`
 * inside it starts at zero, which is exactly what the TTS recorded.
 */
import {readFileSync, writeFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..');
// Em- and en-dashes are breath points in English narration. Without them a clause like
// "not X — but Y" stays one page, and the longest English page ran to 144 characters.
const PUNCT = new Set([...'，。；：、？！,.?!;:\n—–—']);

const readScript = (p) => readFileSync(p, 'utf8');

/** frames out of `## Fn · title (frame n)` headings, with the indented narration */
function narration(md) {
  const out = new Map();
  let cur = null;
  for (const raw of md.split('\n')) {
    const h = /^#{2,3}\s+.*?\(frame\s+(\d+)\)/i.exec(raw);
    if (h) {
      if (cur) out.set(cur.n, cur.text.trim());
      cur = {n: Number(h[1]), text: ''};
      continue;
    }
    if (!cur) continue;
    const m = /^(?: {4,}|\t)(.+)$/.exec(raw);
    // JOIN WITH A SPACE, because that is what gen-voice.py does when it reads the same file.
    // Two parsers of one script with different joining rules is a silent desync: the audio was
    // recorded from the spaced text, this walk counted the unspaced one, and every caption page
    // ended up carrying the NEXT sentence's words — 242 of 242, with no error anywhere.
    if (m) cur.text += (cur.text ? ' ' : '') + m[1].trim();
  }
  if (cur) out.set(cur.n, cur.text.trim());
  return out;
}

function pagesFor(text, words) {
  // THE COORDINATE SYSTEM, stated once because getting it wrong is silent:
  // `concat` is a STRING, so `concat[i]` indexes CHARACTERS; `words[j]` indexes WORDS. The
  // inherited version compared `concat[wi]` to a character while advancing `wi` as a WORD index,
  // and assigned `concat.find(ch, wi)`'s CHARACTER result to that word index — so the walk
  // over-ran the first group and lagged every group after it. All 242 pages were wrong and
  // nothing complained.
  //
  // The correct shape: walk characters, remember the character position of each narration
  // character, then map positions back to words through the index built while joining.
  const concat = words.map((w) => w.text).join('');
  const charToWord = [];                 // concat character position -> word index
  words.forEach((w, j) => { for (let k = 0; k < w.text.length; k += 1) charToWord.push(j); });

  // 1. align the narration text to the spoken stream, character by character
  const posOf = [];                      // narration char -> concat char position
  let p = 0;
  for (const ch of text) {
    if (/\s/.test(ch)) continue;
    if (PUNCT.has(ch)) continue;         // the TTS drops or keeps punctuation inconsistently
    if (concat[p] === ch) { posOf.push(p); p += 1; continue; }
    const j = concat.indexOf(ch, p);     // skip over whatever the TTS normalised away
    if (j === -1) { posOf.push(p); continue; }
    p = j;
    posOf.push(p);
    p += 1;
  }

  // 2. cut at punctuation: a page is a breath, cut only where the speaker breathes
  const pages = [];
  let cur = null;
  const flush = () => { if (cur && cur.to.length) pages.push(cur); cur = null; };
  let idx = 0;                           // narration index, parallel to posOf minus skips
  for (const ch of text) {
    // A space is CONTENT, not a separator to skip. Skipping it is invisible in zh — but in any
    // space-delimited script it concatenates every word on the page: the English captions
    // shipped as "Hasthiseverhappenedtoyou?" and both gates stayed green, because the
    // alignment gate also strips whitespace. The bug and the gate shared one blind spot.
    if (/\s/.test(ch)) { if (cur) cur.text += ch; continue; }
    if (PUNCT.has(ch)) { if (cur) cur.text += ch; flush(); continue; }
    const at = posOf[idx];
    idx += 1;
    if (at === undefined) continue;
    const w = charToWord[at];
    if (!cur) cur = {text: '', to: []};
    if (w === undefined) continue;
    cur.text += ch;
    if (!cur.to.length || cur.to[cur.to.length - 1] !== w) cur.to.push(w);
  }
  flush();

  return pages.map((g, i) => {
    const ws = g.to.map((j) => words[j]);
    const nxt = pages[i + 1] ? pages[i + 1].to[0] : null;
    return {
      startMs: Math.round(ws[0].start * 1000),
      endMs: Math.round(ws[ws.length - 1].end * 1000),
      text: g.text,
      words: ws.map((w) => ({
        text: w.text,
        startMs: Math.round(w.start * 1000),
        endMs: Math.round(w.end * 1000),
      })),
      holdEndMs: Math.round(Math.min(
        nxt !== null ? words[nxt].start : ws[ws.length - 1].end + 1.2,
        ws[ws.length - 1].end + 1.2,
      ) * 1000),
    };
  });
}

const meta = JSON.parse(readFileSync(resolve(ROOT, 'src/generated/audio_meta.json'), 'utf8'));
const texts = narration(readScript(resolve(ROOT, 'script/SCRIPT.md')));

const byFrame = {};
let total = 0;
let longest = 0;
for (const v of meta.voices) {
  const pages = pagesFor(texts.get(v.frame) ?? '', v.words);
  byFrame[v.frame] = pages;
  total += pages.length;
  longest = Math.max(longest, ...pages.map((p) => p.text.length));
}

// THE GATE: each page's punctuation-stripped text must equal its own concatenated words.
// If the two disagree, this walk and the recording disagree about the script, and every caption
// is showing the wrong half-second. It is cheap, and it is the only thing standing between a
// silent desync and a delivered film.
// strip ALL punctuation and symbols, both ASCII and CJK: the page's text carries the
// punctuation the walk cut on, while edge-tts word boundaries never include it. A CJK-only
// range passed the zh gate and failed the en gate on every single page — "?", ".", ",".
const STRIP = /[\s\p{P}\p{S}]/gu;
let mismatched = 0;
for (const [n, pages] of Object.entries(byFrame)) {
  for (const [i, p] of pages.entries()) {
    const want = p.text.replace(STRIP, '');
    const got = p.words.map((w) => w.text).join('').replace(STRIP, '');
    if (want !== got) {
      mismatched += 1;
      if (mismatched <= 5) console.log(`  \u2717 F${n} p${i}: ${want.slice(0, 28)} != ${got.slice(0, 28)}`);
    }
  }
}
if (mismatched) {
  console.error(`\n${mismatched} page(s) whose text and words disagree — narration walk is desynced.`);
  process.exit(1);
}
// A second gate, for space-delimited scripts: the page's text with punctuation removed and
// whitespace COLLAPSED must equal its own words joined with a space. Stripping whitespace — as
// the alignment gate correctly does — cannot see a missing space; this one can, and it is the
// check that would have caught the English captions before they rendered.
const fm = readFileSync(resolve(ROOT, 'script/SCRIPT.md'), 'utf8');
const lang = /^language:\s*(\S+)/m.exec(fm)?.[1] ?? 'zh';
const SPACELESS = /^zh|^ja|^ko/;
const collapse = (t) => t.replace(/[\p{P}\p{S}]/gu, '').replace(/\s+/g, ' ').trim();
let spaced = 0;
if (!SPACELESS.test(lang)) {
  for (const [n, pages] of Object.entries(byFrame)) {
    for (const [i, pg] of pages.entries()) {
      const want = collapse(pg.text);
      const got = collapse(pg.words.map((w) => w.text).join(' '));
      if (want !== got) {
        spaced += 1;
        if (spaced <= 5) console.log(`  \u2717 F${n} p${i}: ${want.slice(0, 40)} != ${got.slice(0, 40)}`);
      }
    }
  }
  if (spaced) {
    console.error(`\n${spaced} page(s) lost their word boundaries — the text would render concatenated.`);
    process.exit(1);
  }
  console.log('gate: word boundaries preserved (space-delimited script) \u2014 pages read as sentences');
} else {
  console.log('gate: CJK script \u2014 space check skipped by language');
}
console.log('gate: every page\'s text equals its own words \u2014 narration walk matches the recording');

writeFileSync(resolve(ROOT, 'src/generated/captions.json'), JSON.stringify(byFrame));
console.log(`${Object.keys(byFrame).length} scenes · ${total} caption pages · longest ${longest} chars`);
for (const [n, pages] of Object.entries(byFrame)) {
  const bad = pages.filter((p) => p.text.length > 34);
  console.log(`  F${String(n).padStart(2, '0')}  ${String(pages.length).padStart(3)} pages` +
    (bad.length ? `  ⚠ ${bad.length} over 34 chars: ${bad[0].text.slice(0, 40)}…` : ''));
}