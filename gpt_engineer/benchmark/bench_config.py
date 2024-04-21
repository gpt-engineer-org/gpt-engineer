from dataclasses import asdict, dataclass, field
from typing import List
from gpt_engineer.core.project_config import read_config, filter_none
from pathlib import Path


@dataclass
class AppsConfig:
    active: bool | None = True
    test_active_indices: List | None = None
    train_active_indices: List | None = None


@dataclass
class MbppConfig:
    active: bool | None = True
    active_indices: List | None = None


class GptmeConfig:
    active: bool | None = True


class GptengConfig:
    active: bool | None = True


@dataclass
class BenchConfig:
    """Configuration for the GPT Engineer CLI and gptengineer.app via `gpt-engineer.toml`."""

    apps: AppsConfig = field(default_factory=AppsConfig)
    mbpp: MbppConfig = field(default_factory=MbppConfig)
    gptme: MbppConfig = field(default_factory=GptmeConfig)
    gpteng: MbppConfig = field(default_factory=GptengConfig)

    @classmethod
    def from_toml(cls, config_file: Path | str):
        if isinstance(config_file, str):
            config_file = Path(config_file)
        config_dict = read_config(config_file)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict):
        apps = config_dict["apps"]
        ind_list_suffix = "active_indices"
        for cat in ["train_", "test_"]:
            apps[cat + ind_list_suffix] = list(
                range(
                    int(apps.get(cat + "indices_first", 0)),
                    int(apps.get(cat + "indices_first", 0))
                    + int(apps.get(cat + "indices_len", 0)),
                )
            )
            apps.pop(cat + "indices_first", None)
            apps.pop(cat + "indices_len", None)

        return cls(
            apps=apps,
            mbpp=config_dict["mbpp"],
            gptme=config_dict["gptme"],
            gpteng=config_dict["gpteng"],
        )
