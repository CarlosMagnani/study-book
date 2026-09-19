# Instagram audio example

Small learning step toward the ingestion side of a video RAG project. It uses
yt-dlp and FFmpeg to save M4A audio plus its complete metadata.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py "https://www.instagram.com/reel/SHORTCODE/"
```

Each run creates:

```text
downloads/<video-id>/
├── audio.m4a
└── audio.info.json
```

Run the check with:

```bash
PYTHONPATH=src python -m unittest
```

Some Instagram posts require login cookies. Add that only when a real URL
fails; yt-dlp supports browser cookies and Netscape-format cookie files.
