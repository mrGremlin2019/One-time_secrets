import os
import redis
from datetime import timedelta
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных окружения

class RedisCache:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            decode_responses=False  # Возвращает bytes (для шифрования)
        )

    def set_secret(self, secret_key: str, encrypted_data: bytes, ttl_seconds: Optional[int] = None):
        """
        Сохраняет секрет в redis.
        - Если `ttl_seconds` не указан, минимальное время жизни — 5 минут.
        """
        min_ttl = 300 # 5 минут
        ttl = max(ttl_seconds, min_ttl) if ttl_seconds else min_ttl
        self.client.setex(secret_key, timedelta(seconds=ttl), encrypted_data)
        return ttl

    def get_secret(self, secret_key: str) -> Optional[bytes]:
        """Получает и удаляет секрет из redis (одноразовый доступ)."""
        encrypted_data = self.client.get(secret_key)
        if encrypted_data:
            self.client.delete(secret_key)  # Удаляем после чтения
        return encrypted_data

    def delete_secret(self, secret_key: str):
        """Принудительно удаляет секрет."""
        self.client.delete(secret_key)

    def get_all_keys(self, pattern="*") -> list:
        """Возвращает все ключи в redis (используется для TTL проверки)."""
        return self.client.keys(pattern)

    def exists(self, secret_key: str) -> bool:
        """Проверяет существование секрета"""
        return bool(self.client.exists(secret_key))

    def get_expired_keys(self) -> List[bytes]:
        """Возвращает ключи с истёкшим TTL (ttl = -1)"""
        return [key for key in self.client.scan_iter("*") if self.client.ttl(key) == -1]