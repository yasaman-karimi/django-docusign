from django.conf import settings
from django.core.cache import cache
from docusign_esign import ApiClient

SCOPES = ["signature", "impersonation"]


def load_private_key(private_key_path):
    """Load private key from a file."""
    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()

    return private_key


def get_access_token():
    """Get the access token"""
    access_token = cache.get("access_token", None)
    if access_token:
        return access_token
    api_client = ApiClient()
    api_client.set_base_path(settings.DOCUSIGN_BASE_PATH)
    response = api_client.request_jwt_user_token(
        client_id=settings.DOCUSIGN_INTEGRATION_KEY,
        user_id=settings.DOCUSIGN_USER_ID,
        oauth_host_name=settings.DOCUSIGN_AUTH_SERVER,
        private_key_bytes=load_private_key(settings.DOCUSIGN_PRIVATE_KEY_PATH),
        expires_in=3600,
        scopes=("signature",),
    )
    access_token = response.access_token
    cache.set("access_token", access_token, timeout=3300)
    return access_token
