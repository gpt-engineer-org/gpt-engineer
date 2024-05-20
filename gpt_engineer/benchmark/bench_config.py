from dataclasses import dataclass, field
from pathlib import Path

from tomlkit.items import Integer

from gpt_engineer.core.project_config import read_config


@dataclass
class AppsConfig:
    active: bool | None = True
    test_start_index: int | None = 0
    test_end_index: int | None = 1
    train_start_index: int | None = 0
    train_end_index: int | None = 0
    examples_per_problem: int | None = 10


@dataclass
class MbppConfig:
    active: bool | None = True
    test_len: int | None = 1
    train_len: int | None = 0


@dataclass
class GptmeConfig:
    active: bool | None = True


@dataclass
class BenchConfig:
    """Configuration for the GPT Engineer CLI and gptengineer.app via `gpt-engineer.toml`."""

    apps: AppsConfig = field(default_factory=AppsConfig)
    mbpp: MbppConfig = field(default_factory=MbppConfig)
    gptme: GptmeConfig = field(default_factory=GptmeConfig)

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
        )

    @staticmethod
    def recursive_resolve(data_dict):
        for key, value in data_dict.items():
            if isinstance(value, Integer):
                data_dict[key] = int(value)
            elif isinstance(value, dict):
                BenchConfig.recursive_resolve(value)

    def to_dict(self):
        dict_config = {
            benchmark_name: {key: val for key, val in spec_config.__dict__.items()}
            for benchmark_name, spec_config in self.__dict__.items()
        }
        BenchConfig.recursive_resolve(dict_config)

        return dict_config
