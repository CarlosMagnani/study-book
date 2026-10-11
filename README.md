# Study Book

Learning project that turns an Instagram reel into a study summary, fully on
this machine: yt-dlp and FFmpeg save the audio, Faster-Whisper transcribes it,
and a local Ollama model writes the analysis.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen3:4b
```

Ollama must be running (`ollama serve`) for the analyze step. See
`docs/free-local-stack.md` for installing it.

## Web interface (POC)

```bash
PYTHONPATH=src python -m study_book.web
```

Open http://127.0.0.1:8000, paste a reel URL, and the page runs the three
stages and shows the result.

## Command line

```bash
PYTHONPATH=src python -m study_book.ingest "https://www.instagram.com/reel/SHORTCODE/"
PYTHONPATH=src python -m study_book.transcribe downloads/<video-id>
PYTHONPATH=src python -m study_book.analyze downloads/<video-id>
```

Run every command from the repository root. Each video gets:

```text
downloads/<video-id>/
├── audio.m4a
├── audio.info.json
├── transcript.json
└── analysis.json
```

## Tests

```bash
PYTHONPATH=src python -m unittest
```

Some Instagram posts require login cookies. Add that only when a real URL
fails; yt-dlp supports browser cookies and Netscape-format cookie files.
