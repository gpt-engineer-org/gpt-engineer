import pytest

from gpt_engineer.core.ai import AI


@pytest.mark.xfail(reason="Constructor assumes API access")
def test_ai():
    ai_instance = AI()
    
    # Assuming method1 should return True
    assert ai_instance.method1() == True, "method1 did not return True"
    
    # Assuming method2 should return "success"
    assert ai_instance.method2() == "success", "method2 did not return 'success'"
