"""Tiny in-memory sliding-window rate limiter for auth endpoints.

Good enough for a single-instance deployment (Render free/starter). For a
multi-instance setup, swap this for a Redis-backed limiter.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

_hits: dict[str, deque] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    # Render sits behind a proxy; prefer the forwarded client IP.
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limiter(scope: str, max_hits: int, window_seconds: int):
    """Return a FastAPI dependency enforcing `max_hits` per `window_seconds` per IP."""

    def dependency(request: Request) -> None:
        key = f"{scope}:{_client_ip(request)}"
        now = time.time()
        q = _hits[key]
        cutoff = now - window_seconds
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= max_hits:
            retry = int(window_seconds - (now - q[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please wait a minute and try again.",
                headers={"Retry-After": str(retry)},
            )
        q.append(now)

    return dependency
