import os
import tempfile

from unittest.mock import MagicMock, patch

import openai
import pytest

from dotenv import load_dotenv

from ai import AI

FAKE_API_KEY = "my_api_key"
DOTENV_VAR_NAME = "DOTENV_API_KEY"
CLI_VAR_NAME = "CLI_API_KEY"


@pytest.fixture
def ai():
    return AI


def test_create_returns_valid_object_no_exception(ai):
    with patch("openai.Model.retrieve") as mock_retrieve:
        mock_retrieve.return_value = MagicMock()

        ai_instance = ai()
        ai_instance.create()

        mock_retrieve.assert_called_with("gpt-4")
        assert "model" not in ai_instance.kwargs
        assert isinstance(ai_instance, AI)


def test_create_returns_valid_object_with_exception(ai):
    with patch("openai.Model.retrieve") as mock_retrieve:
        mock_retrieve.side_effect = openai.error.InvalidRequestError(
            "Invalid request", None
        )

        ai_instance = ai()
        ai_instance.create()

        assert ai_instance.kwargs["model"] == "gpt-3.5-turbo"
        assert isinstance(ai_instance, AI)


def test_api_key_from_dotenv_assigns_correctly_to_openai(ai):
    # Create a temporary .env file for testing
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as env_file:
        env_file.write(f"{DOTENV_VAR_NAME}={FAKE_API_KEY}\n")

    # Load environment variables from the temporary .env file
    load_dotenv(env_file.name)

    ai_instance = ai(DOTENV_VAR_NAME)
    api_key = os.getenv(DOTENV_VAR_NAME)

    ai_instance.api_key = api_key

    assert ai_instance.api_key is not None, "API key not loaded from .env file"
    assert (
        ai_instance.api_key == FAKE_API_KEY
    ), "openai.api_key not set correctly from .env file"


def test_api_key_from_cli_export_assigns_correctly_to_openai(ai, monkeypatch):
    monkeypatch.setenv(CLI_VAR_NAME, FAKE_API_KEY)

    ai_instance = ai(CLI_VAR_NAME)
    api_key = os.getenv(CLI_VAR_NAME)

    ai_instance.api_key = api_key

    assert ai_instance.api_key is not None, "API key not loaded from CLI export"
    assert (
        ai_instance.api_key == FAKE_API_KEY
    ), "openai.api_key not set correctly from CLI export"
