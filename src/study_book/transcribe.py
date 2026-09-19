"""Local transcription (Step 2): audio.m4a -> transcript.json beside it."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from study_book.transcript import Segment, Transcript

# ponytail: model injected so fast tests use a stub; real WhisperModel only in manual runs (Step 5 adds the CLI).


def default_model():
    # pyrefly: ignore [missing-import]
    from faster_whisper import WhisperModel

    return WhisperModel("small", device="cpu", compute_type="int8")


def transcribe(audio: str | Path, model) -> Transcript:
    audio = Path(audio)
    segments, info = model.transcribe(str(audio), beam_size=5)
    segs = [Segment(start=s.start, end=s.end, text=s.text.strip()) for s in segments]
    t = Transcript(
        source_id=audio.parent.name,
        language=getattr(info, "language", None),
        text=" ".join(s.text for s in segs),
        segments=segs,
    )
    t.save(audio.parent / "transcript.json")
    return t


def main(argv: list[str] | None = None, model=None) -> int:
    parser = argparse.ArgumentParser(description="Transcribe audio.m4a to transcript.json.")
    parser.add_argument("dir", type=Path, help="video directory, e.g. downloads/<id>")
    audio = parser.parse_args(argv).dir / "audio.m4a"
    if not audio.exists():
        print(f"error: {audio} not found; run the ingest step first", file=sys.stderr)
        return 1
    transcribe(audio, model or default_model())
    print(f"Wrote {audio.parent / 'transcript.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
