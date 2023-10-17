import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
from gpt_engineer.cli.learning import ask_collection_consent  # Ensure you import your function correctly

# Use a fixture to clean up created files after each test
@pytest.fixture
def cleanup():
    yield
    if Path(".gpte_consent").exists():
        Path(".gpte_consent").unlink()

def test_ask_collection_consent_yes(cleanup):
    with patch("builtins.input", side_effect=["y"]):
        result = ask_collection_consent()
    assert Path(".gpte_consent").exists()
    assert Path(".gpte_consent").read_text() == "true"
    assert result == True

def test_ask_collection_consent_no(cleanup):
    with patch("builtins.input", side_effect=["n"]):
        result = ask_collection_consent()
    assert not Path(".gpte_consent").exists()
    assert result == False

def test_ask_collection_consent_invalid_then_yes(cleanup):
    with patch("builtins.input", side_effect=["invalid", "y"]):
        result = ask_collection_consent()
    assert Path(".gpte_consent").exists()
    assert Path(".gpte_consent").read_text() == "true"
    assert result == True

def test_ask_collection_consent_invalid_then_no(cleanup):
    with patch("builtins.input", side_effect=["invalid", "n"]):
        result = ask_collection_consent()
    assert not Path(".gpte_consent").exists()
    assert result == False

# You can add more tests as required, for example, handling multiple invalid inputs etc.
