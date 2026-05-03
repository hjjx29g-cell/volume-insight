import unittest
import numpy as np
import sys
sys.path.append('../scripts')
from compute_obv import compute_obv
from compute_adl import compute_adl
from compute_vwap import compute_vwap

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

if __name__ == '__main__':
    unittest.main()
