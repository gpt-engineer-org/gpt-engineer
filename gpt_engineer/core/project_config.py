"""
Functions for reading and writing the `gpt-engineer.toml` configuration file.

The `gpt-engineer.toml` file is a TOML file that contains project-specific configuration used by the GPT Engineer CLI and gptengineer.app.
"""
from dataclasses import asdict, dataclass, field
from pathlib import Path

import tomlkit

default_config_filename = "config.toml"

example_config = """
[run]
build = "npm run build"
test = "npm run test"
lint = "quick-lint-js"

[paths]
base = "./frontend"  # base directory to operate in (for monorepos)
src = "./src"        # source directory (under the base directory) from which context will be retrieved

[gptengineer-app]  # this namespace is used for gptengineer.app, may be used for internal experiments
project_id = "..."

# we support multiple OpenAPI schemas, used as context for the LLM
openapi = [
    { url = "https://api.gptengineer.app/openapi.json" },
    { url = "https://some-color-translating-api/openapi.json" },
]
"""


@dataclass
class _PathsConfig:
    base: str | None = None
    src: str | None = None


@dataclass
class _ApiConfig:
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None


@dataclass
class _ModelConfig:
    model_name: str | None = None
    temperature: float | None = None
    azure_endpoint: str | None = None


@dataclass
class _ImproveConfig:
    is_linting: bool | None = None
    is_file_selection: bool | None = None


def filter_none(d: dict) -> dict:
    # Drop None values and empty dictionaries from a dictionary
    return {
        k: v
        for k, v in (
            (k, filter_none(v) if isinstance(v, dict) else v)
            for k, v in d.items()
            if v is not None
        )
        if not (isinstance(v, dict) and not v)  # Check for non-empty after filtering
    }


@dataclass
class Config:
    """Configuration for the GPT Engineer CLI and gptengineer.app via `gpt-engineer.toml`."""

    paths: _PathsConfig = field(default_factory=_PathsConfig)
    api_config: _ApiConfig = field(default_factory=_ApiConfig)
    model_config: _ModelConfig = field(default_factory=_ModelConfig)
    improve_config: _ImproveConfig = field(default_factory=_ImproveConfig)

    @classmethod
    def from_toml(cls, config_file: Path | str):
        if isinstance(config_file, str):
            config_file = Path(config_file)
        config_dict = read_config(config_file)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict):
        paths = _PathsConfig(**config_dict.get("paths", {}))
        api_config = _ApiConfig(**config_dict.get("api_config", {}))
        model_config = _ModelConfig(**config_dict.get("model_config", {}))
        improve_config = _ImproveConfig(**config_dict.get("improve_config", {}))

        return cls(
            paths=paths,
            api_config=api_config,
            model_config=model_config,
            improve_config=improve_config,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["gptengineer-app"] = d.pop("gptengineer_app", None)

        # Drop None values and empty dictionaries
        # Needed because tomlkit.dumps() doesn't handle None values,
        # and we don't want to write empty sections.
        d = filter_none(d)

        return d

    def to_toml(self, config_file: Path | str, save=True) -> str:
        """Write the configuration to a TOML file."""
        if isinstance(config_file, str):
            config_file = Path(config_file)

        # Load the TOMLDocument and overwrite it with the new values
        config = read_config(config_file)
        default_config = Config().to_dict()
        for k, v in self.to_dict().items():
            # only write values that are already explicitly set, or that differ from defaults
            if k in config or v != default_config[k]:
                if isinstance(v, dict):
                    config[k] = {
                        k2: v2
                        for k2, v2 in v.items()
                        if (
                            k2 in config[k]
                            or default_config.get(k) is None
                            or v2 != default_config[k].get(k2)
                        )
                    }
                else:
                    config[k] = v

        toml_str = tomlkit.dumps(config)
        if save:
            with open(config_file, "w") as f:
                f.write(toml_str)

        return toml_str


def read_config(config_file: Path) -> tomlkit.TOMLDocument:
    """Read the configuration file"""
    assert config_file.exists(), f"Config file {config_file} does not exist"
    with open(config_file, "r") as f:
        return tomlkit.load(f)
