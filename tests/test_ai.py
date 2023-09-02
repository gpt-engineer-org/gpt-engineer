import pytest

from gpt_engineer.ai import AI
from gpt_engineer.ai import AI, generate_diff, apply_diff


@pytest.mark.xfail(reason="Constructor assumes API access")
def test_ai():
    AI()
    # TODO Assert that methods behave and not only constructor.

def test_generate_diff():
    original_code = "def hello():\n    print('Hello, world!')"
    refactored_code = "def hello():\n    print('Hello, everyone!')"
    diff = generate_diff(original_code, refactored_code)
    assert "-    print('Hello, world!')" in diff
    assert "+    print('Hello, everyone!')" in diff

def test_apply_diff():
    codebase = "def hello():\n    print('Hello, world!')"
    diff = "--- original\n+++ refactored\n@@ -1,2 +1,2 @@\n def hello():\n-    print('Hello, world!')\n+    print('Hello, everyone!')"
    updated_codebase = apply_diff(codebase, diff)
    assert "def hello():\n    print('Hello, everyone!')" in updated_codebase
