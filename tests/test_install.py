"""
Tests for successful import of the package and its modules
"""
import traceback


# Test that the package can be imported
def test_import():
    try:
        from gpt_engineer import (
            ai,
            domain,
            chat_to_files,
            steps,
            db,
        )
    except ImportError as e:
        # tb = traceback.format_exc()
        assert False, f"Failed to import {e.name}"
