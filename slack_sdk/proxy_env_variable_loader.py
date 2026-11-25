"""Internal module for loading proxy-related env variables."""

import logging
import os
import re
from typing import Optional
from urllib.parse import urlsplit

_default_logger = logging.getLogger(__name__)


def load_http_proxy_from_env(logger: logging.Logger = _default_logger) -> Optional[str]:
    proxy_url = (
        os.environ.get("HTTPS_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
    )
    if proxy_url is None:
        return None
    if len(proxy_url.strip()) == 0:
        # If the value is an empty string, the intention should be unsetting it
        logger.debug("The Slack SDK ignored the proxy env variable as an empty value is set.")
        return None

    logger.debug(f"HTTP proxy URL has been loaded from an env variable: {_redact_credentials(proxy_url)}")
    return proxy_url


def _redact_credentials(url: str) -> str:
    """Replaces the user info (e.g., user:password@) in a URL so that it can be safely logged."""
    if "@" in url:
        scheme = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url)
        prefix = scheme.group(0) if scheme else ""
        return f"{prefix}***@{url.rpartition('@')[2]}"
    try:
        urlsplit(url)
    except ValueError:
        return "(unparsable URL)"
    return url
