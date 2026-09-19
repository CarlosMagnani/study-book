import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from study_book.transcribe import transcribe
from study_book.transcript import Transcript


class StubModel:
    def transcribe(self, path, beam_size=5):
        assert Path(path).name == "audio.m4a"
        segments = [
            SimpleNamespace(start=0.0, end=1.2, text=" hello"),
            SimpleNamespace(start=1.2, end=2.0, text="world "),
        ]
        return segments, SimpleNamespace(language="en")


class TranscribeTest(unittest.TestCase):
    def test_writes_transcript_beside_audio(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            audio = Path(d) / "DdbtpWSRhWJ" / "audio.m4a"
            audio.parent.mkdir()
            audio.touch()
            t = transcribe(audio, StubModel())
            self.assertEqual(t.source_id, "DdbtpWSRhWJ")
            self.assertEqual(t.language, "en")
            self.assertEqual(t.text, "hello world")
            self.assertEqual(Transcript.load(audio.parent / "transcript.json"), t)


if __name__ == "__main__":
    unittest.main()
