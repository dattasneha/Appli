from datetime import timedelta, datetime
import hashlib
import hmac
import secrets
import uuid
from typing import Optional

import jwt

from src.config import Config

ACCESS_TOKEN_EXPIRY = 900
_PBKDF2_ITERATIONS = 100_000


def create_access_token(user_data: dict, expiry: timedelta = None) -> str:
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())
    token = jwt.encode(payload=payload, key=Config.ACCESS_TOKEN_KEY, algorithm="HS256")
    return token


def hash_password(password: str) -> str:
    """Hash a plaintext password using PBKDF2-HMAC-SHA256.

    Returns a string in the form: pbkdf2_sha256$iterations$salt_hex$hash_hex
    """
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored PBKDF2 hash."""
    try:
        algo, iter_s, salt_hex, hash_hex = hashed.split("$")
    except ValueError:
        return False
    if algo != "pbkdf2_sha256":
        return False
    try:
        iterations = int(iter_s)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), iterations
    )
    return hmac.compare_digest(dk.hex(), hash_hex)


def decode_token(token: str) -> Optional[dict]:
    """Decode a JWT access token and return the payload.

    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, Config.ACCESS_TOKEN_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None



