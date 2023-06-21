import pytest

from gpt_engineer.ai import GPT


@pytest.mark.xfail(reason="Constructor assumes API access")
def test_ai():
    GPT()
    # TODO Assert that methods behave and not only constructor.
