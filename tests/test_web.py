import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from study_book.transcript import Transcript
from study_book.web import make_handler, run_stage


def fake_run(stage: str, body: dict, downloads: Path) -> str:
    if stage == "analyze":
        raise RuntimeError("ollama is not running")
    return f"{stage}:{body['id']}"


class WebTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.downloads = Path(self.tmp.name)
        video = self.downloads / "DdbtpWSRhWJ"
        video.mkdir()
        (video / "audio.info.json").write_text('{"title": "Video by someone"}')
        Transcript(source_id=video.name, language="pt", text="oi", segments=[]).save(
            video / "transcript.json"
        )

        handler = make_handler(self.downloads, fake_run)
        handler.log_message = lambda *args: None
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def post(self, path: str, body: dict):
        request = urllib.request.Request(self.base + path, data=json.dumps(body).encode())
        return json.load(urllib.request.urlopen(request))

    def test_serves_the_page(self) -> None:
        page = urllib.request.urlopen(self.base + "/").read().decode()
        self.assertIn("<title>Study Book</title>", page)

    def test_lists_videos_with_their_artifacts(self) -> None:
        (video,) = json.load(urllib.request.urlopen(self.base + "/api/videos"))
        self.assertEqual(video["id"], "DdbtpWSRhWJ")
        self.assertEqual(video["title"], "Video by someone")
        self.assertEqual(video["transcript"]["language"], "pt")
        self.assertIsNone(video["analysis"])

    def test_post_runs_the_named_stage(self) -> None:
        reply = self.post("/api/transcribe", {"id": "DdbtpWSRhWJ"})
        self.assertEqual(reply, {"id": "transcribe:DdbtpWSRhWJ"})

    def test_failed_stage_returns_its_error(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.post("/api/analyze", {"id": "DdbtpWSRhWJ"})
        self.assertEqual(caught.exception.code, 500)
        self.assertEqual(json.load(caught.exception), {"error": "ollama is not running"})

    def test_run_stage_rejects_ids_outside_downloads(self) -> None:
        for video_id in ("..", "missing", ""):
            with self.assertRaises(LookupError):
                run_stage("transcribe", {"id": video_id}, self.downloads)


if __name__ == "__main__":
    unittest.main()
