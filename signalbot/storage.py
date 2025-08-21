try:
    import redis
except ModuleNotFoundError:
    pass

import json
import sqlite3
from typing import Any
from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def read(self, key: str) -> Any:
        pass

    @abstractmethod
    def save(self, key: str, object: Any) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass


class StorageError(Exception):
    pass


class SQLiteStorage(Storage):
    def __init__(self, database: str = ":memory:"):
        self._sqlite = sqlite3.connect(database)
        self._sqlite.execute(
            "CREATE TABLE IF NOT EXISTS signalbot (key text unique, value text)"
        )

    def exists(self, key: str) -> bool:
        return self._sqlite.execute(
            "SELECT EXISTS(SELECT 1 FROM signalbot WHERE key = ?)", [key]
        ).fetchone()[0]

    def read(self, key: str) -> Any:
        try:
            result = self._sqlite.execute(
                "SELECT value FROM signalbot WHERE key = ?", [key]
            ).fetchone()[0]
            return json.loads(result)
        except Exception as e:
            raise StorageError(f"SQLite load failed: {e}")

    def save(self, key: str, object: Any) -> None:
        try:
            value = json.dumps(object)
            self._sqlite.execute(
                "INSERT INTO signalbot VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=?",
                [key, value, value],
            )
            self._sqlite.commit()
        except Exception as e:
            raise StorageError(f"SQLite save failed: {e}")

    def delete(self, key: str) -> None:
        try:
            self._sqlite.execute("DELETE FROM signalbot WHERE key = ?", [key])
            self._sqlite.commit()
        except Exception as e:
            raise StorageError(f"SQLite delete failed: {e}")


class RedisStorage(Storage):
    def __init__(self, host: str, port: int):
        self._redis = redis.Redis(host=host, port=port, db=0)

    def exists(self, key: str) -> bool:
        return self._redis.exists(key)

    def read(self, key: str) -> Any:
        try:
            result_bytes = self._redis.get(key)
            result_str = result_bytes.decode("utf-8")
            result_dict = json.loads(result_str)
            return result_dict
        except Exception as e:
            raise StorageError(f"Redis load failed: {e}")

    def save(self, key: str, object: Any) -> None:
        try:
            object_str = json.dumps(object)
            self._redis.set(key, object_str)
        except Exception as e:
            raise StorageError(f"Redis save failed: {e}")

    def delete(self, key: str) -> None:
        try:
            self._redis.delete(key)
        except Exception as e:
            raise StorageError(f"Redis delete failed: {e}")
