# -*- coding: utf-8 -*-

import unittest
from src.core.iso5817 import ISO5817Evaluator


class TestISO5817Evaluator(unittest.TestCase):
    def setUp(self):
        self.eval = ISO5817Evaluator()

    def test_crack_rejected_all_levels(self):
        for level in ("B", "C", "D"):
            ok, reason = self.eval.evaluate("defect_crack", 10.0, 5.0, 1.0, 5.0, level=level)
            self.assertFalse(ok)

    def test_incomplete_penetration_level_d(self):
        # D allows limited IP
        ok, _ = self.eval.evaluate("defect_ip", 10.0, 3.0, 1.0, 3.0, level="D")
        self.assertTrue(ok)
        ok, _ = self.eval.evaluate("defect_ip", 10.0, 20.0, 1.0, 3.0, level="D")
        self.assertFalse(ok)

    def test_incomplete_penetration_level_b(self):
        ok, _ = self.eval.evaluate("defect_ip", 10.0, 1.0, 1.0, 1.0, level="B")
        self.assertFalse(ok)

    def test_incomplete_fusion_levels(self):
        # Not permitted at B or C
        for level in ("B", "C"):
            ok, _ = self.eval.evaluate("defect_if", 10.0, 1.0, 1.0, 1.0, level=level)
            self.assertFalse(ok)

    def test_porosity_limits(self):
        # D level allows larger pores than B
        ok_b, _ = self.eval.evaluate("defect_porosity", 10.0, 4.0, 4.0, 5.0, level="B")
        ok_d, _ = self.eval.evaluate("defect_porosity", 10.0, 4.0, 4.0, 5.0, level="D")
        self.assertFalse(ok_b)
        self.assertTrue(ok_d)

    def test_undercut_depth(self):
        # B max 0.5 mm depth; D max 1.5 mm
        ok_b, _ = self.eval.evaluate("defect_undercut", 10.0, 10.0, 1.0, 5.0, level="B")
        self.assertFalse(ok_b)
        ok_d, _ = self.eval.evaluate("defect_undercut", 10.0, 10.0, 1.0, 5.0, level="D")
        self.assertTrue(ok_d)

    def test_burn_through(self):
        # Not permitted at B/C; limited at D
        ok_b, _ = self.eval.evaluate("defect_burn_through", 10.0, 1.0, 1.0, 1.0, level="B")
        self.assertFalse(ok_b)
        ok_d, _ = self.eval.evaluate("defect_burn_through", 10.0, 1.0, 1.0, 1.0, level="D")
        self.assertTrue(ok_d)

    def test_slag_width(self):
        ok_d, _ = self.eval.evaluate("defect_slag", 10.0, 10.0, 2.0, 5.0, level="D")
        self.assertTrue(ok_d)
        ok_b, _ = self.eval.evaluate("defect_slag", 10.0, 10.0, 2.0, 5.0, level="B")
        self.assertFalse(ok_b)

    def test_accept_message_references_level(self):
        ok, reason = self.eval.evaluate("defect_slag", 10.0, 5.0, 0.5, 2.0, level="C", lang="en")
        self.assertTrue(ok)
        self.assertIn("level C", reason)


if __name__ == "__main__":
    unittest.main()