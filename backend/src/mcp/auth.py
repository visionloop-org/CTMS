"""
Cryptographic API Key Authenticator & Rate Limiting Middleware
Enforces SHA-256 token hashing, RBAC scopes, and leaky-bucket rate limiting.
Conforms to docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md.
"""

import hashlib
import time
from typing import Dict, List, Optional, Set
from pydantic import BaseModel


class APIKeyMetadata(BaseModel):
    key_id: str
    tenant_id: str
    key_name: str
    key_prefix: str
    key_hash: str
    allowed_scopes: List[str]
    rate_limit_rpm: int = 300
    is_active: bool = True
    expires_at: Optional[float] = None


class RateLimiterBucket:
    """In-memory leaky bucket rate limiter per API key."""

    def __init__(self, rpm: int):
        self.rpm = rpm
        self.capacity = float(rpm)
        self.tokens = float(rpm)
        self.last_update = time.time()
        self.leak_rate = rpm / 60.0  # Tokens replenished per second

    def consume(self) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Replenish tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.leak_rate)

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class APIKeyAuthenticator:
    """Manages and authenticates ctms_live_... API keys."""

    def __init__(self):
        # Key hash -> APIKeyMetadata
        self._keys_by_hash: Dict[str, APIKeyMetadata] = {}
        # Key hash -> RateLimiterBucket
        self._rate_limiters: Dict[str, RateLimiterBucket] = {}

    @staticmethod
    def hash_key(raw_token: str) -> str:
        """Computes SHA-256 hexadecimal hash of the API key."""
        return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()

    def register_key(self, raw_token: str, metadata: APIKeyMetadata):
        """Registers a key with its SHA-256 hash."""
        h = self.hash_key(raw_token)
        metadata.key_hash = h
        self._keys_by_hash[h] = metadata
        self._rate_limiters[h] = RateLimiterBucket(metadata.rate_limit_rpm)

    def authenticate(
        self,
        raw_token: str,
        required_scope: Optional[str] = None,
    ) -> APIKeyMetadata:
        """
        Validates API key authenticity, expiration, scopes, and rate limits.
        Raises PermissionError or ValueError on rejection.
        """
        if not raw_token or not raw_token.startswith("ctms_live_"):
            raise ValueError("Invalid API key format. Expected 'ctms_live_<32_hex>'")

        key_hash = self.hash_key(raw_token)
        meta = self._keys_by_hash.get(key_hash)

        if not meta or not meta.is_active:
            raise PermissionError("API key not found or inactive")

        if meta.expires_at and time.time() > meta.expires_at:
            raise PermissionError("API key has expired")

        # Check required scope
        if required_scope:
            if required_scope not in meta.allowed_scopes and "admin:all" not in meta.allowed_scopes:
                raise PermissionError(f"API key lacks required scope: {required_scope}")

        # Check rate limiter
        limiter = self._rate_limiters.get(key_hash)
        if limiter and not limiter.consume():
            raise RuntimeError(f"Rate limit exceeded (Max {meta.rate_limit_rpm} req/min). Try again later.")

        return meta


api_key_auth = APIKeyAuthenticator()

# Register a default mock key for testing
api_key_auth.register_key(
    "ctms_live_mock_test_key_001_enterprise",
    APIKeyMetadata(
        key_id="k-001",
        tenant_id="tenant-apex-gas",
        key_name="Apex Gas Primary ERP Key",
        key_prefix="ctms_live_mock",
        key_hash="",
        allowed_scopes=["cylinders:read", "dispatch:write", "safety:verify", "mcp:access"],
        rate_limit_rpm=600,
    ),
)
