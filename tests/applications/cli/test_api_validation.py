"""
Tests for API key validation functionality in the CLI.
"""

import os
import unittest
from unittest.mock import patch

import typer

from gpt_engineer.applications.cli.main import (
    validate_api_configuration,
    validate_api_key_format,
)


class TestValidateApiKeyFormat(unittest.TestCase):
    """Test the validate_api_key_format function."""

    def test_valid_openai_key(self):
        """Test validation of a valid OpenAI API key."""
        is_valid, error_msg = validate_api_key_format(
            "OPENAI_API_KEY", "sk-proj-1234567890abcdefghijklmnop"
        )
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_valid_openai_key_sk_format(self):
        """Test validation of OpenAI key with sk- prefix."""
        is_valid, error_msg = validate_api_key_format(
            "OPENAI_API_KEY", "sk-1234567890abcdefghijklmnop"
        )
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_valid_anthropic_key(self):
        """Test validation of a valid Anthropic API key."""
        is_valid, error_msg = validate_api_key_format(
            "ANTHROPIC_API_KEY", "sk-ant-1234567890abcdefghijklmnop"
        )
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_empty_key(self):
        """Test validation of an empty API key."""
        is_valid, error_msg = validate_api_key_format("OPENAI_API_KEY", "")
        self.assertFalse(is_valid)
        self.assertIn("empty", error_msg)

    def test_too_short_key(self):
        """Test validation of a too short API key."""
        is_valid, error_msg = validate_api_key_format("OPENAI_API_KEY", "sk-123")
        self.assertFalse(is_valid)
        self.assertIn("too short", error_msg)

    def test_placeholder_key_your(self):
        """Test detection of placeholder API key starting with 'your-'."""
        is_valid, error_msg = validate_api_key_format(
            "OPENAI_API_KEY", "your-api-key-here"
        )
        self.assertFalse(is_valid)
        self.assertIn("placeholder", error_msg.lower())

    def test_placeholder_key_dots(self):
        """Test detection of placeholder API key '...'."""
        is_valid, error_msg = validate_api_key_format("OPENAI_API_KEY", "...")
        self.assertFalse(is_valid)
        self.assertIn("placeholder", error_msg.lower())

    def test_invalid_openai_key_prefix(self):
        """Test validation fails for OpenAI key without sk- prefix."""
        is_valid, error_msg = validate_api_key_format(
            "OPENAI_API_KEY", "invalid-1234567890abcdefghijklmnop"
        )
        self.assertFalse(is_valid)
        self.assertIn("should start with", error_msg)

    def test_invalid_anthropic_key_prefix(self):
        """Test validation fails for Anthropic key without sk-ant- prefix."""
        is_valid, error_msg = validate_api_key_format(
            "ANTHROPIC_API_KEY", "sk-1234567890abcdefghijklmnop"
        )
        self.assertFalse(is_valid)
        self.assertIn("sk-ant-", error_msg)

    def test_azure_key_no_specific_format(self):
        """Test that Azure keys don't have specific format requirements."""
        is_valid, error_msg = validate_api_key_format(
            "AZURE_OPENAI_API_KEY", "any-valid-length-key-12345"
        )
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")


class TestValidateApiConfiguration(unittest.TestCase):
    """Test the validate_api_configuration function."""

    def test_clipboard_mode_skips_validation(self):
        """Test that clipboard mode skips API key validation."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise an exception even without API keys
            try:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="",
                    llm_via_clipboard=True
                )
            except typer.Exit:
                self.fail("Clipboard mode should skip validation")

    def test_local_model_skips_validation(self):
        """Test that local model mode skips API key validation."""
        with patch.dict(os.environ, {"LOCAL_MODEL": "true"}, clear=True):
            # Should not raise an exception even without API keys
            try:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="",
                    llm_via_clipboard=False
                )
            except typer.Exit:
                self.fail("Local model mode should skip validation")

    def test_missing_openai_key(self):
        """Test validation fails when OpenAI key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(typer.Exit) as context:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="",
                    llm_via_clipboard=False
                )
            self.assertEqual(context.exception.exit_code, 1)

    def test_missing_anthropic_key(self):
        """Test validation fails when Anthropic key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(typer.Exit) as context:
                validate_api_configuration(
                    model="claude-3-opus-20240229",
                    azure_endpoint="",
                    llm_via_clipboard=False
                )
            self.assertEqual(context.exception.exit_code, 1)

    def test_missing_azure_key(self):
        """Test validation fails when Azure key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(typer.Exit) as context:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="https://example.openai.azure.com",
                    llm_via_clipboard=False
                )
            self.assertEqual(context.exception.exit_code, 1)

    def test_valid_openai_key_passes(self):
        """Test validation passes with valid OpenAI key."""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-proj-1234567890abcdefghijklmnop"},
            clear=True
        ):
            try:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="",
                    llm_via_clipboard=False
                )
            except typer.Exit:
                self.fail("Validation should pass with valid OpenAI key")

    def test_valid_anthropic_key_passes(self):
        """Test validation passes with valid Anthropic key."""
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "sk-ant-1234567890abcdefghijklmnop"},
            clear=True
        ):
            try:
                validate_api_configuration(
                    model="claude-3-opus-20240229",
                    azure_endpoint="",
                    llm_via_clipboard=False
                )
            except typer.Exit:
                self.fail("Validation should pass with valid Anthropic key")

    def test_valid_azure_key_passes(self):
        """Test validation passes with valid Azure key."""
        with patch.dict(
            os.environ,
            {"AZURE_OPENAI_API_KEY": "valid-azure-key-1234567890"},
            clear=True
        ):
            try:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="https://example.openai.azure.com",
                    llm_via_clipboard=False
                )
            except typer.Exit:
                self.fail("Validation should pass with valid Azure key")

    def test_invalid_openai_key_format_fails(self):
        """Test validation fails with invalid OpenAI key format."""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "invalid-key-1234567890abcdefghijklmnop"},
            clear=True
        ):
            with self.assertRaises(typer.Exit) as context:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="",
                    llm_via_clipboard=False
                )
            self.assertEqual(context.exception.exit_code, 1)

    def test_placeholder_openai_key_fails(self):
        """Test validation fails with placeholder OpenAI key."""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "your-api-key-here"},
            clear=True
        ):
            with self.assertRaises(typer.Exit) as context:
                validate_api_configuration(
                    model="gpt-4",
                    azure_endpoint="",
                    llm_via_clipboard=False
                )
            self.assertEqual(context.exception.exit_code, 1)

    def test_anthropic_model_name_variations(self):
        """Test that Anthropic keys are validated for various model name formats."""
        test_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "anthropic/claude-3-opus",
        ]
        
        for model in test_models:
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(typer.Exit):
                    validate_api_configuration(
                        model=model,
                        azure_endpoint="",
                        llm_via_clipboard=False
                    )


if __name__ == "__main__":
    unittest.main()

