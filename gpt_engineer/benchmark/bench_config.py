from dataclasses import asdict, dataclass, field
from typing import List
from gpt_engineer.core.project_config import read_config, filter_none
from pathlib import Path


@dataclass
class AppsConfig:
    active: bool | None = True
    test_start_index: int | None = 0
    test_end_index: int | None = 1
    train_start_index: int | None = 0
    train_end_index: int | None = 0


@dataclass
class MbppConfig:
    active: bool | None = True
    test_len: int | None = 1
    train_len: int | None = 0


@dataclass
class GptmeConfig:
    active: bool | None = True


@dataclass
class GptengConfig:
    active: bool | None = True


@dataclass
class BenchConfig:
    """Configuration for the GPT Engineer CLI and gptengineer.app via `gpt-engineer.toml`."""

    apps: AppsConfig = field(default_factory=AppsConfig)
    mbpp: MbppConfig = field(default_factory=MbppConfig)
    gptme: GptmeConfig = field(default_factory=GptmeConfig)
    gpteng: GptengConfig = field(default_factory=GptengConfig)

    @classmethod
    def from_toml(cls, config_file: Path | str):
        if isinstance(config_file, str):
            config_file = Path(config_file)
        config_dict = read_config(config_file)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(
            apps=AppsConfig(**config_dict.get("apps", {})),
            mbpp=MbppConfig(**config_dict.get("mbpp", {})),
            gptme=GptmeConfig(**config_dict.get("gptme", {})),
            gpteng=GptengConfig(**config_dict.get("gpteng", {})),
        )
