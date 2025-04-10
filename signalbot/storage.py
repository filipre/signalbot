try:
    import redis
except ModuleNotFoundError:
    pass

import json
import sqlite3
from typing import Any


class Storage:
    def exists(self, key: str) -> bool:
        raise NotImplementedError

    def read(self, key: str) -> Any:
        raise NotImplementedError

    def save(self, key: str, object: Any):
        raise NotImplementedError


class StorageError(Exception):
    pass


class SQLiteStorage(Storage):
    def __init__(self, database=":memory:"):
        self._sqlite = sqlite3.connect(database)
        self._sqlite.execute(
            "CREATE TABLE IF NOT EXISTS signalbot (key text unique, value text)"
        )

    def exists(self, key):
        return self._sqlite.execute(
            "SELECT EXISTS(SELECT 1 FROM signalbot WHERE key = ?)", [key]
        ).fetchone()[0]

    def read(self, key):
        try:
            result = self._sqlite.execute(
                "SELECT value FROM signalbot WHERE key = ?", [key]
            ).fetchone()[0]
            return json.loads(result)
        except Exception as e:
            raise StorageError(f"SQLite load failed: {e}")

    def save(self, key, object):
        try:
            value = json.dumps(object)
            self._sqlite.execute(
                "INSERT INTO signalbot VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=?",
                [key, value, value],
            )
            self._sqlite.commit()
        except Exception as e:
            raise StorageError(f"SQLite save failed: {e}")


class RedisStorage(Storage):
    def __init__(self, host, port):
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

    def save(self, key: str, object: Any):
        try:
            object_str = json.dumps(object)
            self._redis.set(key, object_str)
        except Exception as e:
            raise StorageError(f"Redis save failed: {e}")
