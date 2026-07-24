import tempfile
import unittest
from pathlib import Path

from app import discover_repositories, normalize_github_url


class CoreTests(unittest.TestCase):
    def test_normalize_https_url(self):
        self.assertEqual(
            normalize_github_url("https://github.com/user/repo.git"),
            "https://github.com/user/repo",
        )

    def test_normalize_ssh_url(self):
        self.assertEqual(
            normalize_github_url("git@github.com:user/repo.git"),
            "https://github.com/user/repo",
        )

    def test_discover_direct_child_repositories(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "alpha" / ".git").mkdir(parents=True)
            (root / "beta").mkdir()
            (root / "gamma" / ".git").mkdir(parents=True)

            found = discover_repositories(root)
            self.assertEqual([path.name for path in found], ["alpha", "gamma"])


if __name__ == "__main__":
    unittest.main()
