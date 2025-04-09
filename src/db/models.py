from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, INET, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Log(Base):
    """Модель для хранения логов действий с секретами."""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(20), nullable=False)  # "create", "read", "delete"
    secret_key = Column(UUID(as_uuid=True), nullable=False)  # UUID из кеша
    ip_address = Column(INET, nullable=False)  # Пример: "127.0.0.1"
    user_agent = Column(String)  # Опционально (например, "Mozilla/5.0")

    request_metadata = Column(JSON)  # Доп. данные в формате JSON:
    # {
    #   "ttl_seconds": 3600,
    #   "has_passphrase": true,
    #   "client_headers": {...}
    # }

    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)  # UTC время

    def __repr__(self):
        return f"<Log(action='{self.action}', secret_key={self.secret_key}, ip={self.ip_address})>"