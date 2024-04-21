from dataclasses import asdict, dataclass, field
from typing import List
from gpt_engineer.core.project_config import read_config, filter_none
from pathlib import Path


@dataclass
class _AppsConfig:
    active: bool | None = True
    test_active_indices: List | None = None
    train_active_indices: List | None = None


@dataclass
class _MbppConfig:
    active: bool | None = True
    active_indices: List | None = None


@dataclass
class BenchConfig:
    """Configuration for the GPT Engineer CLI and gptengineer.app via `gpt-engineer.toml`."""

    apps: _AppsConfig = field(default_factory=_AppsConfig)
    mbpp: _MbppConfig = field(default_factory=_MbppConfig)

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

        mbpp = config_dict["mbpp"]
        mbpp[ind_list_suffix] = list(
            range(
                int(mbpp.get("indices_first", 0)),
                int(mbpp.get("indices_first", 0)) + int(mbpp.get("indices_len", 5)),
            )
        )
        mbpp.pop("indices_len", None)
        mbpp.pop("indices_first", None)

        return cls(apps=apps, mbpp=mbpp)
