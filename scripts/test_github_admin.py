"""Regression checks for GitHub API responses without network or credentials."""

import contextlib
import io
import unittest
from unittest.mock import patch

import github_admin


class PagesConfigurationTest(unittest.TestCase):
    def test_legacy_update_204_refreshes_actual_pages_url(self):
        state = {"owner": "Bage340", "repo": "ryazan-web-demos"}
        pages = {"build_type": "workflow", "html_url": "https://example.invalid/demo/"}
        responses = [{"login": "Bage340"}, {"build_type": "legacy"}, {}, pages]
        with patch.object(github_admin, "credential", return_value="test-credential"), \
                patch.object(github_admin, "load_state", return_value=state), \
                patch.object(github_admin, "save_state") as save, \
                patch.object(github_admin, "api", side_effect=responses) as api, \
                patch("sys.argv", ["github_admin.py", "enable-pages"]), \
                contextlib.redirect_stdout(io.StringIO()):
            github_admin.main()
        self.assertEqual(save.call_args.args[0]["pages_url"], pages["html_url"])
        self.assertEqual(api.call_args.args[1], "/repos/Bage340/ryazan-web-demos/pages")
        self.assertEqual(len(api.call_args.args), 2)


if __name__ == "__main__":
    unittest.main()
