"""
Tests for the sysinfo functionality in the CLI.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from gpt_engineer.applications.cli.main import (
    get_environment_variables,
    get_gpt_engineer_version,
    get_system_info,
    mask_sensitive_value,
)


class TestMaskSensitiveValue(unittest.TestCase):
    """Test the mask_sensitive_value function."""

    def test_mask_api_key_long(self):
        """Test masking a long API key."""
        result = mask_sensitive_value("OPENAI_API_KEY", "sk-proj-1234567890abcdef")
        self.assertIn("sk-p", result)
        self.assertIn("cdef", result)
        self.assertIn("...", result)
        self.assertIn("length:", result)
        self.assertNotIn("1234567890", result)

    def test_mask_api_key_short(self):
        """Test masking a short API key."""
        result = mask_sensitive_value("API_KEY", "short123")
        self.assertEqual(result, "****** (length: 8)")

    def test_non_sensitive_value(self):
        """Test that non-sensitive values are not masked."""
        result = mask_sensitive_value("MODEL_NAME", "gpt-4")
        self.assertEqual(result, "gpt-4")

    def test_sensitive_patterns(self):
        """Test various sensitive patterns are detected."""
        sensitive_keys = [
            "SECRET_KEY",
            "API_TOKEN",
            "PASSWORD",
            "CREDENTIALS",
            "AUTH_TOKEN",
        ]
        for key in sensitive_keys:
            result = mask_sensitive_value(key, "sensitive_value_12345")
            self.assertIn("...", result)
            self.assertIn("length:", result)

    def test_empty_value(self):
        """Test masking an empty sensitive value."""
        result = mask_sensitive_value("API_KEY", "")
        self.assertEqual(result, "")


class TestGetEnvironmentVariables(unittest.TestCase):
    """Test the get_environment_variables function."""

    def test_get_env_vars_with_set_values(self):
        """Test getting environment variables that are set."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sk-test-key-1234567890abcdef",
                "MODEL_NAME": "gpt-4",
                "ANTHROPIC_API_KEY": "anthropic-key-12345",
            },
            clear=True,
        ):
            result = get_environment_variables()

            # Check that relevant vars are present
            self.assertIn("OPENAI_API_KEY", result)
            self.assertIn("MODEL_NAME", result)
            self.assertIn("ANTHROPIC_API_KEY", result)

            # Check that API keys are masked
            self.assertIn("...", result["OPENAI_API_KEY"])
            self.assertNotIn("test-key", result["OPENAI_API_KEY"])

            # Check that non-sensitive values are not masked
            self.assertEqual(result["MODEL_NAME"], "gpt-4")

    def test_get_env_vars_not_set(self):
        """Test getting environment variables that are not set."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_environment_variables()

            # Check that unset vars are marked as "not set"
            self.assertEqual(result["OPENAI_API_KEY"], "not set")
            self.assertEqual(result["MODEL_NAME"], "not set")

    def test_get_env_vars_with_wildcard(self):
        """Test getting environment variables with wildcard patterns."""
        with patch.dict(
            os.environ,
            {
                "GPT_ENGINEER_DEBUG": "true",
                "GPT_ENGINEER_CUSTOM": "value",
                "OTHER_VAR": "should_not_appear",
            },
            clear=True,
        ):
            result = get_environment_variables()

            # Check that GPT_ENGINEER_* vars are captured
            self.assertIn("GPT_ENGINEER_DEBUG", result)
            self.assertIn("GPT_ENGINEER_CUSTOM", result)

            # Check that non-matching vars are not captured
            self.assertNotIn("OTHER_VAR", result)


class TestGetGptEngineerVersion(unittest.TestCase):
    """Test the get_gpt_engineer_version function."""

    @patch("importlib.metadata.version")
    @patch("importlib.metadata.metadata")
    def test_get_version_released(self, mock_metadata, mock_version):
        """Test getting version for a released package."""
        mock_version.return_value = "0.3.1"
        mock_metadata.return_value = {"Installer": "pip"}

        with patch("gpt_engineer.applications.cli.main.Path") as mock_path:
            mock_path.return_value.parent.parent.__truediv__.return_value.exists.return_value = (
                False
            )

            result = get_gpt_engineer_version()

            self.assertEqual(result["version"], "0.3.1")
            self.assertIn("released", result["install_type"].lower())

    @patch("importlib.metadata.version")
    @patch("importlib.metadata.metadata")
    def test_get_version_development(self, mock_metadata, mock_version):
        """Test getting version for a development package."""
        mock_version.return_value = "0.3.1.dev0"
        mock_metadata.return_value = {"Installer": "pip"}

        with patch("gpt_engineer.applications.cli.main.Path") as mock_path:
            mock_path.return_value.parent.parent.__truediv__.return_value.exists.return_value = (
                True
            )

            result = get_gpt_engineer_version()

            self.assertEqual(result["version"], "0.3.1.dev0")
            self.assertIn("development", result["install_type"].lower())

    @patch("importlib.metadata.version")
    def test_get_version_with_git_hash(self, mock_version):
        """Test getting version with git hash (development)."""
        mock_version.return_value = "0.3.1+g1234567"

        result = get_gpt_engineer_version()

        self.assertEqual(result["version"], "0.3.1+g1234567")
        # Should be detected as development due to the + sign
        self.assertIn("development", result["install_type"].lower())

    @patch("importlib.metadata.version")
    def test_get_version_error_handling(self, mock_version):
        """Test error handling when version cannot be determined."""
        mock_version.side_effect = Exception("Package not found")

        result = get_gpt_engineer_version()

        self.assertEqual(result["version"], "unknown")
        self.assertEqual(result["install_type"], "unknown")
        self.assertIn("error", result)


class TestGetSystemInfo(unittest.TestCase):
    """Test the get_system_info function."""

    @patch("gpt_engineer.applications.cli.main.get_installed_packages")
    @patch("gpt_engineer.applications.cli.main.get_environment_variables")
    @patch("gpt_engineer.applications.cli.main.get_gpt_engineer_version")
    def test_get_system_info_structure(
        self, mock_version, mock_env, mock_packages
    ):
        """Test that get_system_info returns the expected structure."""
        mock_version.return_value = {
            "version": "0.3.1",
            "install_type": "released (from pip)",
        }
        mock_env.return_value = {"OPENAI_API_KEY": "sk-...-key (length: 20)"}
        mock_packages.return_value = {"openai": "1.0.0"}

        result = get_system_info()

        # Check that all expected keys are present
        self.assertIn("os", result)
        self.assertIn("os_version", result)
        self.assertIn("architecture", result)
        self.assertIn("python_version", result)
        self.assertIn("gpt_engineer_version", result)
        self.assertIn("environment_variables", result)
        self.assertIn("packages", result)

        # Check that nested structures are correct
        self.assertIsInstance(result["gpt_engineer_version"], dict)
        self.assertIsInstance(result["environment_variables"], dict)

    @patch("gpt_engineer.applications.cli.main.get_installed_packages")
    @patch("gpt_engineer.applications.cli.main.get_environment_variables")
    @patch("gpt_engineer.applications.cli.main.get_gpt_engineer_version")
    def test_get_system_info_values(self, mock_version, mock_env, mock_packages):
        """Test that get_system_info returns valid values."""
        mock_version.return_value = {
            "version": "0.3.1",
            "install_type": "released (from pip)",
        }
        mock_env.return_value = {"MODEL_NAME": "gpt-4"}
        mock_packages.return_value = {"typer": "0.9.0"}

        result = get_system_info()

        # Check that values are not empty
        self.assertIsNotNone(result["os"])
        self.assertIsNotNone(result["python_version"])
        self.assertEqual(
            result["gpt_engineer_version"]["version"], "0.3.1"
        )


if __name__ == "__main__":
    unittest.main()

