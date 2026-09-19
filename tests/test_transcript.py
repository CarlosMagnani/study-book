import tempfile
import unittest
from pathlib import Path

from study_book.transcript import Segment, Transcript


class TranscriptContractTest(unittest.TestCase):
    def test_save_and_load_round_trip(self) -> None:
        t = Transcript(
            source_id="DdbtpWSRhWJ",
            language="en",
            text="hello world",
            segments=[
                Segment(start=0.0, end=1.2, text="hello"),
                Segment(start=1.2, end=2.0, text="world"),
            ],
        )
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "transcript.json"
            t.save(p)
            self.assertEqual(Transcript.load(p), t)


if __name__ == "__main__":
    unittest.main()
