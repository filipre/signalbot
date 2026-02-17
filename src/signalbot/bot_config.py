from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from signalbot.api import ConnectionMode


class RedisConfig(BaseModel):
    type: Literal["redis"] = "redis"
    redis_host: str
    redis_port: int


class SQLiteConfig(BaseModel):
    type: Literal["sqlite"] = "sqlite"
    sqlite_db: str | Path
    check_same_thread: bool = True


class InMemoryConfig(BaseModel):
    type: Literal["in-memory"] = "in-memory"


class BotConfig(BaseModel):
    signal_service: str
    phone_number: str

    storage: RedisConfig | SQLiteConfig | InMemoryConfig | None = None
    retry_interval: int = 1
    download_attachments: bool = True
    connection_mode: ConnectionMode = ConnectionMode.AUTO


def load_config(config: BotConfig | Mapping | Path | str) -> BotConfig:
    if isinstance(config, BotConfig):
        return config

    if isinstance(config, Mapping):
        return BotConfig.model_validate(config)

    if isinstance(config, (str, Path)):
        if isinstance(config, str):
            config = Path(config)
        if config.suffix.lower() == ".json":
            with config.open() as f:
                return BotConfig.model_validate_json(f.read())
        if config.suffix.lower() in [".yaml", ".yml"]:
            with config.open() as f:
                data = yaml.safe_load(f)
            return BotConfig.model_validate(data)

    error_msg = f"Invalid config {config}"
    raise ValueError(error_msg)
