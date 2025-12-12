import os
import ssl
from ssl import SSLContext
from typing import Optional


def has_ssl_env_vars() -> bool:
    """Check if SSL-related environment variables are set"""
    ssl_env_vars = ["SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"]
    return any(os.environ.get(var) for var in ssl_env_vars)


def create_ssl_context_with_certifi_fallback(custom_ssl: Optional[SSLContext] = None) -> Optional[SSLContext]:
    """Create SSL context with certifi fallback for certificate issues

    Priority:
    1. If custom_ssl is provided or SSL env vars are set -> return custom_ssl
    2. If certifi is available -> use certifi's certificate bundle
    3. Otherwise -> return custom_ssl (usually None)

    This helps resolve SSL certificate issues on Windows by using certifi's
    curated certificate bundle when no explicit SSL configuration is provided.
    """
    # Use custom_ssl if provided, or respect SSL environment variables
    if custom_ssl is not None or has_ssl_env_vars():
        return custom_ssl

    # Fall back to certifi if available (helps with Windows SSL issues)
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return custom_ssl
