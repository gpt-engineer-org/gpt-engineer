import unittest
from gpt_engineer.core.default.on_disk_execution_env import OnDiskExecutionEnv
from gpt_engineer.core.default.git_version_manager import GitVersionManager
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE
import tempfile
from unittest.mock import patch, MagicMock


class TestOnDiskExecutionEnv(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env = OnDiskExecutionEnv(GitVersionManager(self.temp_dir.name))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_successful_execution(self):
        entrypoint_content = """
        python -m venv venv
        source venv/bin/activate
        python script.py
        """
        code = {
            ENTRYPOINT_FILE: entrypoint_content,
            "script.py": "print('This is a test script')",
        }
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value.wait.return_value = 0
            process = self.env.popen(code)
            self.assertIsNotNone(process)
            mock_popen.assert_called_once()

    def test_missing_entrypoint(self):
        code = {"script.py": "print('This is a test script')"}
        with self.assertRaises(FileNotFoundError):
            self.env.popen(code)

    def test_keyboard_interrupt_handling(self):
        entrypoint_content = """
        python script.py
        """
        code = {
            ENTRYPOINT_FILE: entrypoint_content,
            "script.py": "print('This is a test script')",
        }
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.wait.side_effect = KeyboardInterrupt
            mock_popen.return_value = mock_process
            self.env.popen(code)
            mock_process.kill.assert_called_once()

    def test_execution_with_output(self):
        entrypoint_content = """
        python script.py
        """
        code = {
            ENTRYPOINT_FILE: entrypoint_content,
            "script.py": "import sys; print('Out'); sys.stderr.write('Error')",
        }
        with patch("subprocess.Popen") as mock_popen:
            process = MagicMock()
            process.wait.return_value = 0
            process.communicate.return_value = (b"Out\n", b"Error\n")
            mock_popen.return_value = process
            process = self.env.popen(code)
            stdout, stderr = process.communicate()
            self.assertEqual(stdout, b"Out\n")
            self.assertEqual(stderr, b"Error\n")


if __name__ == "__main__":
    unittest.main()
