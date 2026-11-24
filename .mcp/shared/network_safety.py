"""Network URL and redirect validation for EMRF MCP science-data adapters."""

from __future__ import annotations

import ipaddress
import socket
import urllib.request
from typing import Any, Callable, Optional
from urllib.parse import urlsplit

MAX_REDIRECTS = 5


def validate_public_https_url(url: str, *, resolve_dns: bool = True) -> str:
    """Reject non-HTTPS, credentialed, non-443, local, private, or multicast targets."""
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid_url") from exc

    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or hostname.lower() == "localhost"
        or hostname.lower().endswith((".localhost", ".local"))
    ):
        raise ValueError("public_https_url_required")

    addresses = []
    try:
        addresses = [ipaddress.ip_address(hostname)]
    except ValueError:
        if resolve_dns:
            try:
                addresses = [
                    ipaddress.ip_address(info[4][0])
                    for info in socket.getaddrinfo(
                        hostname, port or 443, type=socket.SOCK_STREAM
                    )
                ]
            except OSError as exc:
                raise ValueError("hostname_resolution_failed") from exc
            if not addresses:
                raise ValueError("hostname_resolution_failed")

    if any(not address.is_global or address.is_multicast for address in addresses):
        raise ValueError("non_public_network_destination")
    return url


class _SafeHTTPSRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Enforce public HTTPS checks and redirect count caps on every hop."""

    max_redirections = MAX_REDIRECTS

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        redirect_dict = getattr(req, "redirect_dict", {})
        if len(redirect_dict) >= MAX_REDIRECTS:
            raise ValueError("too_many_redirects")
        validate_public_https_url(newurl, resolve_dns=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def safe_https_open(
    request: urllib.request.Request,
    *,
    timeout: float,
    opener: Optional[Callable[..., Any]] = None,
) -> Any:
    """Open an HTTPS request using redirect-validated transport."""
    validate_public_https_url(request.full_url, resolve_dns=(opener is None))
    if opener is not None:
        return opener(request, timeout=timeout)
    safe_opener = urllib.request.build_opener(_SafeHTTPSRedirectHandler)
    return safe_opener.open(request, timeout=timeout)
