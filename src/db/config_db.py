from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator




class Settings(BaseSettings):
    MODE: str  # Для тестовой БД

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @property
    def DB_URL(self):
        return (f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

DB_URL = settings.DB_URL
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)



# def init_db():
#     """Создаёт таблицы в БД. """
#     Base.metadata.create_all(bind=engine)

@contextmanager
def get_db() -> Generator:
    """Генератор сессий для работы с БД."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Database error: {str(e)}")
    finally:
        db.close()
