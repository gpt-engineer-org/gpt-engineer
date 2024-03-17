import tempfile

import pytest

from gpt_engineer.core.project_config import (
    Config,
    _GptEngineerAppConfig,
    _OpenApiConfig,
    example_config,
    filter_none,
)


def test_config_load():
    # write example config to a file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(example_config)

    # load the config from the file
    config = Config.from_toml(f.name)

    assert config.paths.base == "./frontend"
    assert config.paths.src == "./src"
    assert config.run.build == "npm run build"
    assert config.run.test == "npm run test"
    assert config.run.lint == "quick-lint-js"
    assert config.gptengineer_app
    assert config.gptengineer_app.project_id == "..."
    assert config.gptengineer_app.openapi
    assert (
        config.gptengineer_app.openapi[0].url
        == "https://api.gptengineer.app/openapi.json"
    )
    assert (
        config.gptengineer_app.openapi[1].url
        == "https://some-color-translating-api/openapi.json"
    )
    assert config.to_dict()
    assert config.to_toml(f.name, save=False)

    # check that write+read is idempotent
    assert Config.from_toml(f.name) == config


def test_config_defaults():
    config = Config()
    assert config.paths.base is None
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        config.to_toml(f.name)

    # check that read+write is idempotent
    assert Config.from_toml(f.name) == config

    # check that empty (default) config is written as empty string
    toml_str = config.to_toml(f.name, save=False)
    assert toml_str == ""


def test_config_from_dict():
    d = {"gptengineer-app": {"project_id": "..."}}  # minimal example
    config = Config.from_dict(d)
    assert config.gptengineer_app
    assert config.gptengineer_app.project_id == "..."
    config_dict = config.to_dict()

    # check that the config dict matches the input dict exactly (no keys/defaults added)
    assert config_dict == d


def test_config_from_dict_with_openapi():
    # A good test because it has 3 levels of nesting
    d = {
        "gptengineer-app": {
            "project_id": "...",
            "openapi": [
                {"url": "https://api.gptengineer.app/openapi.json"},
            ],
        }
    }
    config = Config.from_dict(d)
    assert config.gptengineer_app
    assert config.gptengineer_app.project_id == "..."
    assert config.gptengineer_app.openapi
    assert (
        config.gptengineer_app.openapi[0].url
        == "https://api.gptengineer.app/openapi.json"
    )


def test_config_load_partial():
    # Loads a partial config, and checks that the rest is not set (i.e. None)
    example_config = """
[gptengineer-app]
project_id = "..."
""".strip()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(example_config)

    config = Config.from_toml(f.name)
    assert config.gptengineer_app
    assert config.gptengineer_app.project_id == "..."
    assert config.to_dict()
    toml_str = config.to_toml(f.name, save=False)
    assert toml_str == example_config

    # check that write+read is idempotent
    assert Config.from_toml(f.name) == config


def test_config_update():
    example_config = """
[gptengineer-app]
project_id = "..."
""".strip()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(example_config)
    config = Config.from_toml(f.name)
    config.gptengineer_app = _GptEngineerAppConfig(
        project_id="...",
        openapi=[_OpenApiConfig(url="https://api.gptengineer.app/openapi.json")],
    )
    config.to_toml(f.name)
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
