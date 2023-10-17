from pathlib import Path
from unittest.mock import patch

from gpt_engineer.cli.learning import check_collection_consent2

# Mock for ask_collection_consent() that always returns True
def mock_ask_collection_consent_true():
    return True

# Mock for ask_collection_consent() that always returns False
def mock_ask_collection_consent_false():
    return False

def setup_function():
    """Remove .gpte_consent file before each test if it exists"""
    path = Path(".gpte_consent")
    if path.exists():
        path.unlink()

def test_check_collection_consent_file_exists_and_true():
    # Setup: create a file with "true"
    path = Path(".gpte_consent")
    path.write_text("true")

    # Verify
    assert check_collection_consent2() == True

def test_check_collection_consent_file_exists_but_not_true():
    # Setup: create a file with text other than "true"
    path = Path(".gpte_consent")
    path.write_text("false")

    with patch("gpt_engineer.cli.learning.ask_collection_consent", mock_ask_collection_consent_true):
        assert check_collection_consent2() == True

    with patch("gpt_engineer.cli.learning.ask_collection_consent", mock_ask_collection_consent_false):
        assert check_collection_consent2() == False

def test_check_collection_consent_file_not_exists():
    with patch("gpt_engineer.cli.learning.ask_collection_consent", mock_ask_collection_consent_true):
        assert check_collection_consent2() == True

    with patch("gpt_engineer.cli.learning.ask_collection_consent", mock_ask_collection_consent_false):
        assert check_collection_consent2() == False

