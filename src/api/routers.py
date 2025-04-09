"""
API маршруты для работы с зашифрованными секретами.
Позволяют создавать, получать (одноразово) и удалять секреты с логированием в PostgreSQL.
"""

import uuid
from fastapi import APIRouter, HTTPException, Request, Depends
from starlette.status import HTTP_404_NOT_FOUND
from uuid import UUID
from src.schemas.secrets import CreateSecretResponse, GetSecretResponse, DeleteSecretResponse, CreateSecretRequest
from src.db.crud import LogCRUD
from src.redis.redis_client import RedisCache
from src.redis.crypto import SecretCrypto

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def get_redis_cache() -> RedisCache:
    """Получает экземпляр RedisCache для DI (зависимостей)."""
    return RedisCache()

def get_crypto() -> SecretCrypto:
    """Получает экземпляр SecretCrypto для шифрования/дешифрования."""
    return SecretCrypto()

def get_log_crud() -> LogCRUD:
    """Получает экземпляр LogCRUD для логирования действий."""
    return LogCRUD()

def filter_headers(headers: dict) -> dict:
    """
    Фильтрует чувствительные заголовки из логов.
    Исключает: Authorization, Cookie, Set-Cookie, X-API-Key.
    """
    sensitive = {"authorization", "cookie", "set-cookie", "x-api-key"}
    return {k: v for k, v in headers.items() if k.lower() not in sensitive}

def log_action(log_crud: LogCRUD, action: str, secret_key: str, request: Request, metadata: dict = None):
    """Унифицированная функция для логирования действия пользователя в PostgreSQL."""
    log_crud.create_log(
        action=action,
        secret_key=secret_key,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
        metadata=metadata or {}
    )


@router.post("/secret", response_model=CreateSecretResponse, summary="Создать секрет", tags=["Secrets"])
def create_secret(
    payload: CreateSecretRequest,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache),
    crypto: SecretCrypto = Depends(get_crypto),
    log_crud: LogCRUD = Depends(get_log_crud)
):
    """
    Создаёт новый зашифрованный секрет с TTL и сохраняет его в redis.

    - Секрет шифруется перед сохранением.
    - TTL регулирует срок хранения (по умолчанию минимум 5 минут).
    - Логируется создание в PostgreSQL.

    Возвращает уникальный ключ для получения секрета.
    """
    secret_key = str(uuid.uuid4())

    try:
        encrypted = crypto.encrypt(payload.secret)
    except Exception as e:
        logger.exception("Encryption failed")
        raise HTTPException(status_code=500, detail="Encryption failed")

    redis_cache.set_secret(secret_key, encrypted, ttl_seconds=payload.ttl_seconds)

    log_action(
        log_crud,
        action="create",
        secret_key=secret_key,
        request=request,
        metadata={
            "ttl_seconds": payload.ttl_seconds,
            "has_passphrase": bool(payload.passphrase),
            "client_headers": filter_headers(dict(request.headers))
        }
    )

    return {"secret_key": secret_key}


@router.get("/secret/{secret_key}", response_model=GetSecretResponse, summary="Получить секрет", tags=["Secrets"])
def get_secret(
    secret_key: UUID,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache),
    crypto: SecretCrypto = Depends(get_crypto),
    log_crud: LogCRUD = Depends(get_log_crud)
):
    """
    Получает и расшифровывает секрет по ключу, после чего удаляет его из redis.

    - Секрет может быть получен **только один раз**.
    - Если ключа не существует — возвращается ошибка 404.
    - Если расшифровка не удалась — ошибка 500.

    Логируется факт прочтения секрета.
    """
    encrypted = redis_cache.get_secret(str(secret_key))
    if not encrypted:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Secret not found or already viewed")

    try:
        decrypted = crypto.decrypt(encrypted)
    except Exception as e:
        logger.exception("Decryption failed")
        raise HTTPException(status_code=500, detail="Decryption failed")

    log_action(log_crud, "read", str(secret_key), request)

    return {"secret": decrypted}


@router.delete("/secret/{secret_key}", response_model=DeleteSecretResponse, summary="Удалить секрет", tags=["Secrets"])
def delete_secret(
    secret_key: UUID,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache),
    log_crud: LogCRUD = Depends(get_log_crud)
):
    """
    Удаляет секрет из redis по ключу.

    - Если ключ не найден — возвращается ошибка 404.


    Используется в случае ручного удаления до автоматического истечения TTL.
    """
    if not redis_cache.exists(str(secret_key)):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Secret not found or already deleted")

    redis_cache.delete_secret(str(secret_key))

    log_action(
        log_crud,
        "delete",
        str(secret_key),
        request,
        metadata={"source": "manual_delete"}
    )

    return {"status": "secret_deleted"}