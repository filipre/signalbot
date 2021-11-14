import redis
import json
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


class InMemoryStorage(Storage):
    def __init__(self):
        self._storage = {}

    def exists(self, key: str) -> bool:
        return key in self._storage

    def read(self, key: str) -> Any:
        try:
            result_str = self._storage[key]
            result_dict = json.loads(result_str)
            return result_dict
        except Exception as e:
            raise StorageError(f"InMemory load failed: {e}")

    def save(self, key: str, object: Any):
        try:
            object_str = json.dumps(object)
            self._storage[key] = object_str
        except Exception as e:
            raise StorageError(f"InMemory save failed: {e}")


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
