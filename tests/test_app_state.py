# -*- coding: utf-8 -*-

import unittest


class TestAppStateCalculations(unittest.TestCase):
    """Tests for the mobile AppState calculation engine (regression coverage
    for the pre-fix silent failures: cap ignored, f_min/ug/sfd_min = 0, and
    compliance always erroring)."""

    def setUp(self):
        from src.mobile.lib.app_state import AppState
        AppState._instance = None
        self.state = AppState()

    def tearDown(self):
        from src.mobile.lib.app_state import AppState
        AppState._instance = None

    def test_w_eff_includes_cap(self):
        # Defaults: SWSI, t=6.02, cap=3.0 -> w_nom=6.02, w_eff=9.02
        self.state.geometry = "swsi"
        r = self.state.run_calculations()
        self.assertAlmostEqual(r["w_nom"], 6.02, places=2)
        self.assertAlmostEqual(r["w_eff"], 9.02, places=2)

    def test_f_min_is_nonzero(self):
        self.state.geometry = "swsi"
        r = self.state.run_calculations()
        self.assertGreater(r["f_min"], 0.0)
        self.assertGreater(r["sfd_min"], 0.0)

    def test_ug_uses_real_geometry(self):
        self.state.geometry = "swsi"
        r = self.state.run_calculations()
        self.assertGreater(r["ug"], 0.0)

    def test_iqi_are_tuples(self):
        r = self.state.run_calculations()
        self.assertIsInstance(r["single_wire_iqi"], tuple)
        self.assertIsInstance(r["duplex_iqi"], tuple)

    def test_compliance_is_evaluated_not_error(self):
        self.state.run_calculations()
        self.assertIn("is_compliant", self.state.compliance)
        # Must NOT be the "always error" fallback
        self.assertNotIn("error", self.state.compliance)

    def test_dwdi_elliptic_exposures_respect_ratio(self):
        # t/De >= 0.12 -> 3 exposures; else 2
        self.state.geometry = "dwdi_elliptic"
        self.state.pipe_od = 50.0
        self.state.pipe_wall = 8.0    # 8/50 = 0.16 >= 0.12 -> 3
        r = self.state.run_calculations()
        self.assertEqual(r["req_exposures"], 3)

        self.state.pipe_od = 100.0
        self.state.pipe_wall = 5.0    # 5/100 = 0.05 < 0.12 -> 2
        r = self.state.run_calculations()
        self.assertEqual(r["req_exposures"], 2)


if __name__ == "__main__":
    unittest.main()