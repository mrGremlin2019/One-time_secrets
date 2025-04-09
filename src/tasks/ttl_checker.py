from datetime import datetime
import asyncio
import logging
from src.redis.redis_client import RedisCache
from src.db.crud import LogCRUD

logger = logging.getLogger(__name__)

class TTLChecker:
    def __init__(self, check_interval: int = 1):
        self.redis = RedisCache()
        self.log_crud = LogCRUD()
        self._already_logged = set()
        self.check_interval = check_interval
        self.source_ip = "127.0.0.1"
        self.user_agent = "ttl_checker"

    def _log_expired_secret(self, key_str: str, ttl: int):
        self.log_crud.create_log(
            action="expired",
            secret_key=key_str,
            ip_address=self.source_ip,
            user_agent=self.user_agent,
            metadata={
                "expired_at": datetime.utcnow().isoformat(),
                "ttl_at_expiry": ttl,
                "source": "ttl_checker"
            }
        )
        logger.info(f"Logged expired secret: {key_str}")

    async def check_expired_secrets(self):
        """Фоновая задача: проверяет TTL ключей и логирует перед удалением."""
        while True:
            try:
                keys = self.redis.client.scan_iter("*")
                for key in keys:
                    key_str = key.decode() if isinstance(key, bytes) else str(key)
                    if key_str in self._already_logged:
                        continue

                    ttl = self.redis.client.ttl(key_str)
                    if ttl in (0, 1) and self.redis.exists(key_str):
                        try:
                            self._log_expired_secret(key_str, ttl)
                            deleted = self.redis.delete_secret(key_str)
                            if deleted:
                                self._already_logged.add(key_str)
                        except Exception as e:
                            logger.error(f"Failed to delete/log key {key_str}: {e}")
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"TTL checker error: {e}")
                await asyncio.sleep(10)
