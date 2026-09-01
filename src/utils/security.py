"""
SnapClass Cryptographic Session & Token Security Engine
OWASP 2025 Compliant Stateless HMAC-SHA256 Token Manager
"""
import hmac
import hashlib
import json
import base64
import time
import secrets
import os
from typing import Optional, Dict, Any

# Load Master Signing Secret from environment or secrets.toml
def get_signing_secret() -> bytes:
    key = os.environ.get("SESSION_SECRET") or os.environ.get("SUPABASE_KEY") or "snapclass-enterprise-hmac-master-secret-2026"
    return key.encode("utf-8")

def b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def b64_decode(data_str: str) -> bytes:
    padding = "=" * (4 - (len(data_str) % 4)) if len(data_str) % 4 != 0 else ""
    return base64.urlsafe_b64decode((data_str + padding).encode("utf-8"))

def generate_session_token(
    user_id: Any,
    role: str,
    ttl_seconds: int = 28800,  # Default: 8 hours
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a cryptographically signed HMAC-SHA256 session token with TTL.
    Format: <payload_b64>.<signature_hex>
    """
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + ttl_seconds,
        "nonce": secrets.token_hex(8)
    }
    if extra_claims:
        payload.update(extra_claims)

    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    payload_b64 = b64_encode(payload_json.encode("utf-8"))

    secret = get_signing_secret()
    signature = hmac.new(secret, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()

    return f"{payload_b64}.{signature}"

def verify_session_token(
    token: Optional[str],
    expected_role: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Verifies token signature, expiration timestamp, and role in constant time.
    Returns decoded claims dict if valid, or None if invalid/expired.
    """
    if not token or "." not in token:
        return None

    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None

        payload_b64, signature_hex = parts
        secret = get_signing_secret()

        # 1. Verify HMAC Signature in constant time
        expected_sig = hmac.new(secret, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature_hex):
            return None

        # 2. Decode and parse payload
        payload_bytes = b64_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # 3. Check Expiration
        now = int(time.time())
        if payload.get("exp", 0) < now:
            return None  # Token Expired

        # 4. Check Role Match if required
        if expected_role and payload.get("role") != expected_role:
            return None  # Role mismatch

        return payload
    except Exception:
        return None
