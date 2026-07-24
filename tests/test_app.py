import unittest
from pathlib import Path

from app import Repo


class RepoTests(unittest.TestCase):
    def test_online_repo_defaults_to_not_local(self):
        repo = Repo(
            name="demo",
            description="Demo repository",
            url="https://github.com/example/demo",
            clone_url="https://github.com/example/demo.git",
            branch="main",
            private=False,
        )
        self.assertIsNone(repo.local_path)
        self.assertFalse(repo.can_pull)
        self.assertEqual(repo.status, "Online")

    def test_local_path_can_be_stored(self):
        path = Path("C:/GitHub/demo")
        repo = Repo("demo", "", "", "", "main", False, local_path=path)
        self.assertEqual(repo.local_path, path)


if __name__ == "__main__":
    unittest.main()
