import os
import base64
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.wrappers import Request


def get_auth_credentials() -> tuple[str, str]:
    valid_username = os.getenv('AMBAR_HTTP_USERNAME')
    valid_password = os.getenv('AMBAR_HTTP_PASSWORD')

    if not valid_username or not valid_password:
        raise RuntimeError('Environment variables AMBAR_HTTP_USERNAME and AMBAR_HTTP_PASSWORD must be set')

    return valid_username, valid_password


def ambar_auth(request_obj: Request) -> None:
    """Middleware function to authenticate a request."""
    auth_header = request_obj.headers.get('Authorization')

    if not auth_header:
        raise PermissionError("Authentication required")

    if not auth_header.startswith('Basic '):
        raise PermissionError("Basic authentication required")

    try:
        valid_username, valid_password = get_auth_credentials()

        encoded_credentials = auth_header.split(' ')[1]
        decoded = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded.split(':')

        if username != valid_username or password != valid_password:
            raise PermissionError("Invalid credentials")

    except Exception as e:
        raise PermissionError(f"Invalid authentication format: {str(e)}")
