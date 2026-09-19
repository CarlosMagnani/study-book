"""Local transcript analysis (Step 4): transcript.json -> analysis.json via Ollama."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from study_book.analysis import Analysis
from study_book.transcript import Transcript

# ponytail: `complete` injected so fast tests use a stub; real Ollama only in manual runs (Step 5 adds the CLI).

PROMPT = (
    "Analyze the following video transcript and respond with JSON only "
    "(keys: topic, summary, key_points, timestamps with start/end/label):\n\n{text}"
)


def ollama_complete(model: str = "qwen3:4b"):
    import ollama  # pyrefly: ignore [missing-import]

    schema = Analysis.model_json_schema()

    def complete(prompt: str) -> str:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            format=schema,
            options={"temperature": 0},
        )
        return response.message.content or ""

    return complete


def analyze(transcript_path: str | Path, complete) -> Analysis:
    transcript_path = Path(transcript_path)
    text = Transcript.load(transcript_path).text
    analysis = Analysis.model_validate_json(complete(PROMPT.format(text=text)))
    analysis.save(transcript_path.parent / "analysis.json")
    return analysis


def main(argv: list[str] | None = None, complete=None) -> int:
    parser = argparse.ArgumentParser(description="Analyze transcript.json to analysis.json.")
    parser.add_argument("dir", type=Path, help="video directory, e.g. downloads/<id>")
    transcript = parser.parse_args(argv).dir / "transcript.json"
    if not transcript.exists():
        print(f"error: {transcript} not found; run the transcribe step first", file=sys.stderr)
        return 1
    analyze(transcript, complete or ollama_complete())
    print(f"Wrote {transcript.parent / 'analysis.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
