from contextlib import contextmanager
from src.db.config_db import get_db
from src.db.models import Log
from typing import Dict, Any


class LogCRUD:
    """Класс для всех операций с логами в PostgreSQL"""

    @contextmanager
    def _get_db_session(self):
        """Использует генератор сессий из config_db"""
        with get_db() as db:
            yield db

    def create_log(
            self,
            action: str,
            secret_key: str,
            ip_address: str,
            user_agent: str = None,
            metadata: Dict[str, Any] = None
    ) -> None:
        """
        Создает запись в логах.

        Args:
            action: create/read/delete
            secret_key: UUID секрета
            ip_address: IP клиента
            user_agent: User-Agent
            metadata: Доп. метаданные
        """
        with self._get_db_session() as db:
            log = Log(
                action=action,
                secret_key=secret_key,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata or {}
            )
            db.add(log)
            db.commit()
