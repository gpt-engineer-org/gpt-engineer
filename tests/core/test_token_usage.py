import base64
import csv
import io
import os

from io import StringIO
from pathlib import Path

from langchain.schema import HumanMessage, SystemMessage
from PIL import Image

from gpt_engineer.core.token_usage import Tokenizer, TokenUsageLog


def test_format_log():
    # arrange
    token_usage_log = TokenUsageLog("gpt-4")
    request_messages = [
        SystemMessage(content="my system message"),
        HumanMessage(content="my user prompt"),
    ]
    response = "response from model"

    # act
    token_usage_log.update_log(request_messages, response, "step 1")
    token_usage_log.update_log(request_messages, response, "step 2")
    csv_log = token_usage_log.format_log()

    # assert
    csv_rows = list(csv.reader(StringIO(csv_log)))

    assert len(csv_rows) == 3

    assert all(len(row) == 7 for row in csv_rows)


def test_usage_cost():
    # arrange
    token_usage_log = TokenUsageLog("gpt-4")
    request_messages = [
        SystemMessage(content="my system message"),
        HumanMessage(content="my user prompt"),
    ]
    response = "response from model"

    # act
    token_usage_log.update_log(request_messages, response, "step 1")
    token_usage_log.update_log(request_messages, response, "step 2")
    usage_cost = token_usage_log.usage_cost()

    # assert
    assert usage_cost > 0


def test_image_tokenizer():
    # Arrange
    token_usage_log = Tokenizer("gpt-4")
    image_path = Path(__file__).parent.parent / "test_data" / "mona_lisa.jpg"
    # Check if the image file exists
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Act
    with Image.open(image_path) as img:
        # Convert RGBA to RGB
        if img.mode == "RGBA":
            img = img.convert("RGB")

        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Calculate the token cost of the base64 encoded image
    image_token_cost = token_usage_log.num_tokens_for_base64_image(image_base64)

    # Assert
    assert image_token_cost == 1105


def test_list_type_message_with_image():
    # Arrange
    token_usage_log = TokenUsageLog("gpt-4")

    request_messages = [
        SystemMessage(content="My system message"),
        HumanMessage(
            content=[
                {"type": "text", "text": "My user message"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII",
                        "detail": "low",
                    },
                },
            ]
        ),
    ]
    response = "response from model"

    # Act
    token_usage_log.update_log(request_messages, response, "list message with image")

    # Since this is the first (and only) log entry, the in-step total tokens should match our expected total
    expected_total_tokens = 106

    # Assert
    assert (
        token_usage_log.log()[-1].in_step_total_tokens == expected_total_tokens
    ), f"Expected {expected_total_tokens} tokens, got {token_usage_log.log()[-1].in_step_total_tokens}"
