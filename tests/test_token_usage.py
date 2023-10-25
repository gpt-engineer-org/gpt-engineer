import csv
from io import StringIO
from gpt_engineer.core.token_usage import TokenUsageLog, TokenUsage
from langchain.schema import AIMessage, HumanMessage, SystemMessage


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
