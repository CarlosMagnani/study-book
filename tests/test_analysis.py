import tempfile
import unittest
from pathlib import Path

import pydantic

from study_book.analysis import Analysis


class AnalysisContractTest(unittest.TestCase):
    def test_valid_data_saves_and_loads(self) -> None:
        a = Analysis(
            topic="raspagem na guarda lacada",
            summary="Video ensina uma raspagem a partir da laçada.",
            key_points=["lacar o braco", "trocar os pes"],
            timestamps=[{"start": 0.0, "end": 7.0, "label": "inicio"}],
        )
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "analysis.json"
            a.save(p)
            self.assertEqual(Analysis.load(p), a)

    def test_malformed_data_fails_clearly(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            Analysis(topic="x", key_points=["ok"])
        with self.assertRaises(pydantic.ValidationError):
            Analysis(topic="x", summary="y", key_points="nao-uma-lista")


if __name__ == "__main__":
    unittest.main()
