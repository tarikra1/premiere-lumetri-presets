import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from premiere_lumetri_presets.core import compute_ducking_envelope, generate_lumetri_jsx


class TestPremiereLumetriPresets(unittest.TestCase):
    def test_generate_jsx_contains_calibrated_values(self) -> None:
        jsx = generate_lumetri_jsx("golden_hour", video_track_index=2)
        self.assertIn("videoTracks[2]", jsx)
        self.assertIn('"Temperature": 11.0', jsx)
        self.assertIn("OK:golden_hour", jsx)

    def test_ducking_envelope_dips_during_speech(self) -> None:
        kf = compute_ducking_envelope([(1.0, 4.0)], total_duration=6.0)
        gains = [g for _, g in kf]
        self.assertIn(-25.0, gains)
        self.assertEqual(kf[0], (0.0, -16.5))
        self.assertEqual(kf[-1], (6.0, -16.5))


if __name__ == "__main__":
    unittest.main()
