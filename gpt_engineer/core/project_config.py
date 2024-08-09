from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

import tomlkit

default_config_filename = "config.toml"

example_config = """
# API Configuration
[API]
OPENAI_API_KEY = "..."
ANTHROPIC_API_KEY = "..."

# Model configurations
[model]
model_name = "gpt-4o"
temperature = 0.1
azure_endpoint = ""

# improve mode Configuration
[improve]
is_linting = false
is_file_selection = true

# Git Filter Configuration
[git_filter]
file_extensions = ["py", "toml", "md"]

# Self-Healing Mechanism Configuration
[self_healing]
retry_attempts = 1
"""


@dataclass
class Config:
    """Configuration for the GPT Engineer project"""

    api_config: Dict[str, Any] = field(default_factory=dict)
    model_config: Dict[str, Any] = field(default_factory=dict)
    improve_config: Dict[str, Any] = field(default_factory=dict)
    git_filter_config: Dict[str, Any] = field(default_factory=dict)
    self_healing_config: Dict[str, Any] = field(default_factory=dict)
    other_sections: Dict[str, Any] = field(
        default_factory=dict
    )  # To handle any other sections dynamically

    @classmethod
    def from_toml(cls, config_file: Path | str):
        if isinstance(config_file, str):
            config_file = Path(config_file)
        config_dict = read_config(config_file)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict):
        api_config = config_dict.get("API", {})
        model_config = config_dict.get("model", {})
        improve_config = config_dict.get("improve", {})
        git_filter_config = config_dict.get("git_filter", {})
        self_healing_config = config_dict.get("self_healing", {})

        # Extract other sections not explicitly handled
        handled_keys = {"API", "model", "improve", "git_filter", "self_healing"}
        other_sections = {k: v for k, v in config_dict.items() if k not in handled_keys}

        return cls(
            api_config=api_config,
            model_config=model_config,
            improve_config=improve_config,
            git_filter_config=git_filter_config,
            self_healing_config=self_healing_config,
            other_sections=other_sections,
        )

    def to_dict(self) -> dict:
        d = {
            "API": self.api_config,
            "model": self.model_config,
            "improve": self.improve_config,
            "git_filter": self.git_filter_config,
            "self_healing": self.self_healing_config,
        }
        d.update(self.other_sections)  # Add other dynamic sections

        # Drop None values and empty dictionaries
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
            if k in config or v != default_config.get(k):
                if isinstance(v, dict):
                    config[k] = {
                        k2: v2
                        for k2, v2 in v.items()
                        if (
                            k2 in config.get(k, {})
                            or default_config.get(k) is None
                            or v2 != default_config.get(k, {}).get(k2)
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


def filter_none(d: dict) -> dict:
    """Drop None values and empty dictionaries from a dictionary"""
    return {
        k: v
        for k, v in (
            (k, filter_none(v) if isinstance(v, dict) else v)
            for k, v in d.items()
            if v is not None
        )
        if not (isinstance(v, dict) and not v)  # Check for non-empty after filtering
    }
