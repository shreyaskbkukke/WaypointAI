import requests
import base64
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from jwt import decode as jwt_decode, get_unverified_header, InvalidTokenError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        jwks_url: str,
        audience: str | None = None,
        issuer: str | None = None,
    ):
        super().__init__(app)
        self.jwks_url = jwks_url
        self.audience = audience
        self.issuer = issuer
        self._jwks = self._fetch_jwks()

    def _fetch_jwks(self) -> dict[str, dict]:
        resp = requests.get(self.jwks_url)
        resp.raise_for_status()
        return { key["kid"]: key for key in resp.json().get("keys", []) }

    def _jwk_to_pubkey(self, jwk: dict) -> rsa.RSAPublicKey:
        def _b64url_decode(val: str) -> bytes:
            padding = '=' * (-len(val) % 4)
            return base64.urlsafe_b64decode(val + padding)

        n = int.from_bytes(_b64url_decode(jwk["n"]), "big")
        e = int.from_bytes(_b64url_decode(jwk["e"]), "big")
        public_numbers = rsa.RSAPublicNumbers(e, n)
        return public_numbers.public_key(default_backend())

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        logger.info(f"JWT Middleware: Processing request to {path}")

        # Skip JWT for MCP handshake and mounted servers
        if (path.endswith("/mcp") and request.method in ("GET", "POST")) or \
            path.startswith("/mcp/") or \
            path in ["/docs", "/openapi.json", "/favicon.ico"] or \
            path.startswith("/static/") or \
            any(path.startswith(f"/{slug}") for slug in getattr(request.app.state, 'mounted_servers', set())):
                logger.info(f"JWT Middleware: Skipping verification for {path}")
                return await call_next(request)
        logger.info(f"JWT Middleware: Verifying token for {path}")

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            parts = auth.split(" ", 1)
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise HTTPException(401, "Invalid Authorization header format")
            token = parts[1].strip()
        else:
            token = request.query_params.get("token")

        if not token:
            raise HTTPException(401, "Missing token")

        try:
            header = get_unverified_header(token)
            jwk = self._jwks.get(header["kid"]) or self._fetch_jwks().get(header["kid"])
            if not jwk:
                raise HTTPException(401, "Unknown JWK kid")

            pubkey = self._jwk_to_pubkey(jwk)
            payload = jwt_decode(
                token,
                pubkey,
                audience=self.audience,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )
            logger.info(f"JWT Middleware: Token verified successfully for user: {payload.get('sub', 'unknown')}")
            request.state.user = payload

        except (InvalidTokenError, KeyError) as e:
            logger.error(f"JWT Middleware: Token validation failed: {e}")
            raise HTTPException(401, f"Token validation error: {e}")

        return await call_next(request)
