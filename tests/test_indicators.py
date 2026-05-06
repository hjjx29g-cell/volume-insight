import unittest
import numpy as np
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from compute_obv import compute_obv
from compute_adl import compute_adl
from compute_vwap import compute_vwap
from analyzer_main import analyze

class TestVolumeIndicators(unittest.TestCase):
    def test_obv_basic(self):
        close = np.array([10, 11, 10, 12])
        volume = np.array([100, 200, 150, 300])
        obv = compute_obv(close, volume)
        expected = [0, 200, 50, 350]
        np.testing.assert_array_equal(obv, expected)

    def test_adl_basic(self):
        high = np.array([11, 12, 11, 13])
        low = np.array([9, 10, 9, 11])
        close = np.array([10, 11, 10, 12])
        volume = np.array([100, 200, 150, 300])
        adl = compute_adl(high, low, close, volume)
        self.assertEqual(len(adl), len(close))

    def test_vwap_cumulative(self):
        high = np.array([10, 11, 12])
        low = np.array([8, 9, 10])
        close = np.array([9, 10, 11])
        volume = np.array([100, 100, 100])
        vwap = compute_vwap(high, low, close, volume)
        np.testing.assert_allclose(vwap, [9.0, 9.5, 10.0])

    def test_analyzer_signal_contract(self):
        rows = [
            {"date": "2026-01-01", "high": 11, "low": 9, "close": 10, "volume": 1000},
            {"date": "2026-01-02", "high": 12, "low": 10, "close": 11, "volume": 1200},
            {"date": "2026-01-03", "high": 13, "low": 11, "close": 12, "volume": 1300},
            {"date": "2026-01-04", "high": 14, "low": 12, "close": 13, "volume": 1400},
            {"date": "2026-01-05", "high": 15, "low": 13, "close": 14, "volume": 1500},
        ]
        result = analyze(rows, stock_code="TEST", target="示例公司")

        self.assertIn(result["direction"], {"bullish", "bearish", "neutral"})
        self.assertEqual(result["source"], "volume_price_momentum_analysis")
        self.assertEqual(result["signal_type"], "technical")
        self.assertEqual(result["stock_code"], "TEST")
        self.assertIn("meta", result)
        self.assertEqual(result["meta"]["output_version"], "0.1")
        self.assertEqual(result["meta"]["skill_name"], "volume_price_momentum_analysis")
        self.assertIn(result["meta"]["risk_level"], {"low", "medium", "high"})
        self.assertIn(result["meta"]["time_horizon"], {"short", "mid", "long"})
        self.assertGreaterEqual(len(result["signals"]), 1)
        self.assertGreaterEqual(len(result["meta"]["evidence"]), 1)

if __name__ == '__main__':
    unittest.main()
