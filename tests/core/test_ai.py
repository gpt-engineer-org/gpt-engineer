import os

from unittest.mock import patch

from langchain.chat_models.base import BaseChatModel
from langchain_community.chat_models.fake import FakeListChatModel

from gpt_engineer.core.ai import AI


def mock_create_chat_model(self) -> BaseChatModel:
    return FakeListChatModel(responses=["response1", "response2", "response3"])


def test_start(monkeypatch):
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")

    # act
    response_messages = ai.start("system prompt", "user prompt", step_name="step name")

    # assert
    assert response_messages[-1].content == "response1"


def test_next(monkeypatch):
    # arrange
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")
    response_messages = ai.start("system prompt", "user prompt", step_name="step name")

    # act
    response_messages = ai.next(
        response_messages, "next user prompt", step_name="step name"
    )

    # assert
    assert response_messages[-1].content == "response2"


def test_token_logging(monkeypatch):
    # arrange
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")

    # act
    response_messages = ai.start("system prompt", "user prompt", step_name="step name")
    usageCostAfterStart = ai.token_usage_log.usage_cost()
    ai.next(response_messages, "next user prompt", step_name="step name")
    usageCostAfterNext = ai.token_usage_log.usage_cost()

    # assert
    assert usageCostAfterStart > 0
    assert usageCostAfterNext > usageCostAfterStart


def test_minimax_model_creation(monkeypatch):
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("MiniMax-M2.7")

    # act
    response_messages = ai.start("system prompt", "user prompt", step_name="step name")

    # assert
    assert response_messages[-1].content == "response1"
    assert ai.token_usage_log.is_minimax_model()
    assert not ai.token_usage_log.is_openai_model()


def test_minimax_temperature_constraint():
    """Test that MiniMax temperature is clamped to avoid zero."""
    ai_instance = AI.__new__(AI)
    ai_instance.temperature = 0.0
    ai_instance.model_name = "MiniMax-M2.7"
    ai_instance.azure_endpoint = None
    ai_instance.streaming = True
    ai_instance.vision = False

    with patch.dict(os.environ, {"MINIMAX_API_KEY": "test-key"}):
        with patch("gpt_engineer.core.ai.ChatOpenAI") as mock_chat:
            mock_chat.return_value = FakeListChatModel(responses=["response"])
            ai_instance._create_chat_model()
            # Verify temperature was clamped above 0
            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["temperature"] >= 0.01


def test_minimax_missing_api_key():
    """Test that MiniMax raises error when API key is missing."""
    ai_instance = AI.__new__(AI)
    ai_instance.temperature = 0.1
    ai_instance.model_name = "MiniMax-M2.7"
    ai_instance.azure_endpoint = None
    ai_instance.streaming = True
    ai_instance.vision = False

    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("MINIMAX_API_KEY", None)
        try:
            ai_instance._create_chat_model()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "MINIMAX_API_KEY" in str(e)
