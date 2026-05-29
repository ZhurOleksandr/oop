"""
Unit tests for auth utilities.
Run: pytest backend/tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from auth import hash_password, verify_password, create_access_token
from jose import jwt
from config import get_settings

settings = get_settings()


class TestPasswordHashing:

    def test_hash_and_verify_correct(self):
        hashed = hash_password("password123")
        assert verify_password("password123", hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("password123")
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_is_different_each_time(self):
        """bcrypt uses random salt — two hashes must differ."""
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2

    def test_hash_starts_with_bcrypt_prefix(self):
        hashed = hash_password("password123")
        assert hashed.startswith("$2b$")

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("something", hashed) is False


class TestJWT:

    def test_token_created_and_decoded(self):
        token = create_access_token({"sub": "user-id-123", "role": "doctor"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "user-id-123"
        assert payload["role"] == "doctor"

    def test_token_has_expiry(self):
        token = create_access_token({"sub": "test"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload

    def test_invalid_token_raises(self):
        from jose import JWTError
        with pytest.raises(JWTError):
            jwt.decode("invalid.token.here", settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    def test_wrong_secret_raises(self):
        from jose import JWTError
        token = create_access_token({"sub": "test"})
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret", algorithms=[settings.ALGORITHM])
