"""Analysis contract (Step 3): validated shape for topic, summary, key points."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

# ponytail: timestamps stay a plain optional list; richer spans only if Step 4 model output needs them.


class SourceTimestamp(BaseModel):
    start: float
    end: float
    label: str = ""


class Analysis(BaseModel):
    topic: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    key_points: list[str] = []
    timestamps: list[SourceTimestamp] = []

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2) + "\n")

    @classmethod
    def load(cls, path: str | Path) -> Analysis:
        return cls.model_validate_json(Path(path).read_text())
