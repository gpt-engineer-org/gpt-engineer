from gpt_engineer.core.ai import AI
from langchain.chat_models.fake import FakeListChatModel
from langchain.chat_models.base import BaseChatModel
import copy


def test_start(monkeypatch):
    """
    Test function for the AI system.
    This test sets up a fake LLM and tests that the start method successfully returns a response
    """

    # arrange
    def mock_create_chat_model(self) -> BaseChatModel:
        return FakeListChatModel(responses=["response1", "response2", "response3"])

    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("fake")

    # act
    response_messages = ai.start("system prompt", "user prompt", "step name")

    # assert
    assert response_messages[-1].content == "response1"


def test_next(monkeypatch):
    """
    Test function for the AI system.
    This test sets up a fake LLM and tests that the start method successfully returns a response
    """

    # arrange
    def mock_create_chat_model(self) -> BaseChatModel:
        return FakeListChatModel(responses=["response1", "response2", "response3"])

    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("fake")
    response_messages = ai.start("system prompt", "user prompt", "step name")

    # act
    response_messages = ai.next(
        response_messages, "next user prompt", step_name="step name"
    )

    # assert
    assert response_messages[-1].content == "response2"


def test_token_logging(monkeypatch):
    """
    Test function for the AI system.
    This test sets up a fake LLM and tests that the start method successfully returns a response
    """

    # arrange
    def mock_create_chat_model(self) -> BaseChatModel:
        return FakeListChatModel(responses=["response1", "response2", "response3"])

    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("fake")

    # act
    initial_token_counts = (
        ai.cumulative_prompt_tokens,
        ai.cumulative_completion_tokens,
        ai.cumulative_total_tokens,
    )
    response_messages = ai.start("system prompt", "user prompt", "step name")
    token_counts_1 = (
        ai.cumulative_prompt_tokens,
        ai.cumulative_completion_tokens,
        ai.cumulative_total_tokens,
    )
    ai.next(response_messages, "next user prompt", step_name="step name")
    token_counts_2 = (
        ai.cumulative_prompt_tokens,
        ai.cumulative_completion_tokens,
        ai.cumulative_total_tokens,
    )

    # assert
    assert initial_token_counts == (0, 0, 0)

    assert_all_greater_than(
        token_counts_1, (1, 1, 1)
    )  # all the token counts are greater than 1

    assert_all_greater_than(
        token_counts_2, token_counts_1
    )  # all counts in token_counts_2 greater than token_counts_1


def assert_all_greater_than(left, right):
    assert all(x > y for x, y in zip(left, right))
