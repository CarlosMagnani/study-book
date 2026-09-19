import tempfile
import unittest
from pathlib import Path

import pydantic

from study_book.analyze import analyze, main
from study_book.analysis import Analysis
from study_book.transcript import Segment, Transcript


def make_transcript(path: Path) -> None:
    Transcript(
        source_id=path.parent.name,
        language="pt",
        text="um raspinho da guarda lacada",
        segments=[Segment(start=0.0, end=7.0, text="um raspinho da guarda lacada")],
    ).save(path)


class AnalyzeTest(unittest.TestCase):
    def test_writes_analysis_beside_transcript(self) -> None:
        def complete(prompt: str) -> str:
            assert "um raspinho" in prompt
            return (
                '{"topic": "raspagem", "summary": "Raspagem da lacada.", '
                '"key_points": ["lacar o braco"], "timestamps": []}'
            )

        with tempfile.TemporaryDirectory() as d:
            tp = Path(d) / "DdbtpWSRhWJ" / "transcript.json"
            tp.parent.mkdir()
            make_transcript(tp)
            a = analyze(tp, complete)
            self.assertEqual(a.topic, "raspagem")
            self.assertEqual(Analysis.load(tp.parent / "analysis.json"), a)

    def test_invalid_model_output_raises_and_saves_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tp = Path(d) / "DdbtpWSRhWJ" / "transcript.json"
            tp.parent.mkdir()
            make_transcript(tp)
            with self.assertRaises(pydantic.ValidationError):
                analyze(tp, lambda prompt: '{"topic": "x"}')
            self.assertFalse((tp.parent / "analysis.json").exists())


GOOD_JSON = (
    '{"topic": "raspagem", "summary": "Raspagem da lacada.", '
    '"key_points": ["lacar o braco"], "timestamps": []}'
)


class AnalyzeCommandTest(unittest.TestCase):
    def test_missing_transcript_names_transcribe_step(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main([d], complete=lambda prompt: GOOD_JSON), 1)

    def test_command_writes_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tp = Path(d) / "DdbtpWSRhWJ" / "transcript.json"
            tp.parent.mkdir()
            make_transcript(tp)
            self.assertEqual(main([str(tp.parent)], complete=lambda prompt: GOOD_JSON), 0)
            self.assertTrue((tp.parent / "analysis.json").exists())


if __name__ == "__main__":
    unittest.main()
