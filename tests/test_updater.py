# -*- coding: utf-8 -*-

import os
import ssl
import unittest


class TestUpdater(unittest.TestCase):
    """Tests for the update checker SSL handling and version parsing."""

    def setUp(self):
        from src.core.updater import UpdateChecker, _ssl_context, compare_versions
        self.UpdateChecker = UpdateChecker
        self.ssl_context = _ssl_context
        self.compare_versions = compare_versions

    def test_ssl_context_is_verified(self):
        ctx = self.ssl_context()
        self.assertIsInstance(ctx, ssl.SSLContext)
        self.assertFalse(ctx.check_hostname is False and ctx.verify_mode == ssl.CERT_NONE,
                         "SSL context must perform certificate verification")

    def test_ssl_context_uses_certifi_when_available(self):
        try:
            import certifi
        except ImportError:
            self.skipTest("certifi not installed")
        ctx = self.ssl_context()
        cafile = certifi.where()
        self.assertTrue(os.path.exists(cafile), "certifi CA bundle must exist")

    def test_update_checker_init(self):
        checker = self.UpdateChecker(repo="owner/repo", current_version="1.0.0")
        self.assertEqual(checker.repo, "owner/repo")
        self.assertIn("api.github.com", checker.api_url)

    def test_compare_versions(self):
        self.assertEqual(self.compare_versions("1.3.3", "1.3.4"), -1)
        self.assertEqual(self.compare_versions("1.3.4", "1.3.3"), 1)
        self.assertEqual(self.compare_versions("1.3.4", "1.3.4"), 0)
        self.assertEqual(self.compare_versions("v1.3.4", "1.3.4"), 0)

    def test_parse_version_handles_prefix(self):
        checker = self.UpdateChecker()
        self.assertEqual(checker._parse_version("v1.3.4"), (1, 3, 4))
        self.assertEqual(checker._parse_version("1.3.4"), (1, 3, 4))


if __name__ == "__main__":
    unittest.main()
