"""Web POC (Step 8): one local page that runs the three stages from a browser."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from study_book import analyze, ingest, transcribe

# ponytail: stdlib http.server only, and `run` injected so fast tests use a stub; a framework only if the POC outgrows one page.

PAGE = Path(__file__).with_name("web.html")


def video_dir(downloads: Path, video_id: str) -> Path:
    if video_id not in {p.name for p in downloads.glob("*") if p.is_dir()}:
        raise LookupError(f"unknown video: {video_id}")
    return downloads / video_id


def read_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def describe(folder: Path) -> dict:
    info = read_json(folder / "audio.info.json") or {}
    return {
        "id": folder.name,
        "title": info.get("title", ""),
        "transcript": read_json(folder / "transcript.json"),
        "analysis": read_json(folder / "analysis.json"),
    }


def run_stage(stage: str, body: dict, downloads: Path) -> str:
    if stage == "ingest":
        return ingest.download(ingest.instagram_url(body["url"])).name
    folder = video_dir(downloads, body["id"])
    if stage == "transcribe":
        transcribe.transcribe(folder / "audio.m4a", transcribe.default_model())
    elif stage == "analyze":
        analyze.analyze(folder / "transcript.json", analyze.ollama_complete())
    else:
        raise LookupError(f"unknown stage: {stage}")
    return folder.name


def make_handler(downloads: Path, run=run_stage):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status: int, body: bytes, content_type: str = "application/json") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/":
                self.reply(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/api/videos":
                videos = [describe(p) for p in sorted(downloads.glob("*")) if p.is_dir()]
                self.reply(200, json.dumps(videos).encode())
            else:
                self.reply(404, b'{"error": "not found"}')

        def do_POST(self) -> None:
            try:
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                video_id = run(self.path.removeprefix("/api/"), body, downloads)
                self.reply(200, json.dumps({"id": video_id}).encode())
            except Exception as error:
                self.reply(500, json.dumps({"error": str(error)}).encode())

    return Handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the local web POC.")
    parser.add_argument("--port", type=int, default=8000)
    port = parser.parse_args(argv).port
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(Path("downloads")))
    print(f"Open http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
