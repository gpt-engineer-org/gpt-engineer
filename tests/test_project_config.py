import tempfile

import pytest

from gpt_engineer.core.project_config import Config, example_config, filter_none


def test_config_load():
    # Write example config to a file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(example_config)

    # Load the config from the file
    config = Config.from_toml(f.name)

    assert config.api_config["OPENAI_API_KEY"] == "..."
    assert config.api_config["ANTHROPIC_API_KEY"] == "..."
    assert config.model_config["model_name"] == "gpt-4o"
    assert config.model_config["temperature"] == 0.1
    assert config.improve_config["is_linting"] is False
    assert config.improve_config["is_file_selection"] is True
    assert config.to_dict()
    assert config.to_toml(f.name, save=False)

    # Check that write+read is idempotent
    assert Config.from_toml(f.name) == config


def test_config_defaults():
    config = Config()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        config.to_toml(f.name)

    # check that read+write is idempotent
    assert Config.from_toml(f.name) == config

    # check that empty (default) config is written as empty string
    toml_str = config.to_toml(f.name, save=False)
    assert toml_str == ""


def test_config_from_dict():
    d = {"improve": {"is_linting": "..."}}  # Minimal example
    config = Config.from_dict(d)
    assert config.improve_config["is_linting"] == "..."
    config_dict = config.to_dict()

    # Check that the config dict matches the input dict exactly (no keys/defaults added)
    assert config_dict == d


def test_config_load_partial():
    # Loads a partial config, and checks that the rest is not set (i.e., None)
    partial_config = """
[improve]
is_linting = "..."
""".strip()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(partial_config)

    config = Config.from_toml(f.name)
    assert config.improve_config["is_linting"] == "..."
    assert config.to_dict()
    toml_str = config.to_toml(f.name, save=False)
    assert toml_str.strip() == partial_config

    # Check that write+read is idempotent
    assert Config.from_toml(f.name) == config


def test_config_update():
    initial_config = """
[improve]
is_linting = "..."
""".strip()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(initial_config)

    config = Config.from_toml(f.name)
    config.improve_config = {"is_linting": False, "is_file_selection": True}
    config.to_toml(f.name)

    # Check that updated values are written and read correctly
    assert Config.from_toml(f.name) == config


@pytest.mark.parametrize(
    "input_dict,expected",
    [
        ({"a": 1, "b": None}, {"a": 1}),
        ({"a": 1, "b": {"c": None, "d": 2}}, {"a": 1, "b": {"d": 2}}),
        ({"a": 1, "b": {}}, {"a": 1}),
        ({"a": 1, "b": {"c": None}}, {"a": 1}),
        (
            {"a": {"b": {"c": None}}, "d": {"e": {"f": 2}}, "g": None},
            {"d": {"e": {"f": 2}}},
        ),
        (
            {"a": 1, "b": {"c": None, "d": {"e": None, "f": {}}}, "g": {"h": 2}},
            {"a": 1, "g": {"h": 2}},
        ),
    ],
)
def test_filter_none(input_dict, expected):
    assert filter_none(input_dict) == expected
