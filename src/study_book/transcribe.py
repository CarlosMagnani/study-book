"""Local transcription (Step 2): audio.m4a -> transcript.json beside it."""

from __future__ import annotations

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
