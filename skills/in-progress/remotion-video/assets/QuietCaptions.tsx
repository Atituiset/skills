import {useCurrentFrame, useVideoConfig} from 'remotion';

export type CaptionWord = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
};
export type CaptionPage = {
  startMs: number;
  endMs: number;
  text: string;
  words: CaptionWord[];
};

/** Mount once inside the scene whose local audio timing these pages follow. */
export function QuietCaptions({pages, fontFamily, bottomInset}: {
  pages: CaptionPage[];
  fontFamily: string;
  bottomInset?: number;
}) {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const now = frame / fps * 1000;
  const page = pages.find(p => now >= p.startMs && now < p.endMs);
  if (!page) return null;
  return <div style={{
    position: 'absolute', left: width * 0.047, right: width * 0.047,
    bottom: bottomInset ?? height * 24 / 1080,
    fontFamily, fontSize: height * 34 / 1080, lineHeight: 1.35,
    textAlign: 'center', color: '#DCE6EE', textShadow: '0 2px 6px #050C18',
    pointerEvents: 'none',
  }}>{page.text}</div>;
}
