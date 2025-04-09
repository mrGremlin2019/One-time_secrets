"""
Pydantic-схемы для сериализации и валидации данных, передаваемых в API.
"""

from pydantic import BaseModel, Field
from typing import Optional

class CreateSecretRequest(BaseModel):
    """
    Запрос на создание секрета.
    """
    secret: str
    passphrase: Optional[str] = None
    ttl_seconds: Optional[int] = Field(default=None, gt=0)

class CreateSecretResponse(BaseModel):
    """
    Ответ после создания секрета.
    """
    secret_key: str

class GetSecretResponse(BaseModel):
    """
    Ответ на получение секрета.
    """
    secret: str

class DeleteSecretResponse(BaseModel):
    """
    Ответ после удаления секрета.
    """
    status: str