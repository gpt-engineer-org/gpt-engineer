import pytest

from gpt_engineer.ai_with_guidance import AIwithGuidance


@pytest.mark.xfail(reason="Constructor assumes API access")
def test_ai():
    AIwithGuidance()
    # TODO Assert that methods behave and not only constructor.
