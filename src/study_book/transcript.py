"""Transcript contract (Step 1): stable JSON beside the video.

Shape (downloads/<id>/transcript.json):
{"source_id": str, "language": str | None, "text": str,
 "segments": [{"start": float, "end": float, "text": str}]}
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

# ponytail: stdlib dataclasses only, no pydantic until Step 3 analysis contract needs strict validation.


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    source_id: str
    language: str | None
    text: str
    segments: list[Segment]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Transcript:
        return cls(
            source_id=d["source_id"],
            language=d.get("language"),
            text=d["text"],
            segments=[Segment(**s) for s in d["segments"]],
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    @classmethod
    def load(cls, path: str | Path) -> Transcript:
        return cls.from_dict(json.loads(Path(path).read_text()))
