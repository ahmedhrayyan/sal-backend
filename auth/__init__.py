from functools import wraps
from flask import request, _request_ctx_stack, current_app
from jose import jwt
from datetime import datetime, timedelta


class AuthError(Exception):
    """ Base class for all auth exceptions """

    def __init__(self, description: str, code: int):
        self.description = description
        self.code = code


def get_token_auth_header() -> str:
    """ get token from current request Authorization header """

    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            "Authorization header is expected", 401)
    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthError(
            "Authorization header must start with Bearer", 401)
    elif len(parts) == 1:
        raise AuthError(
            "Token not found", 401)
    elif len(parts) > 2:
        raise AuthError(
            "Authorization header must be Bearer token", 401)
    token = parts[1]
    return token


def verify_jwt_in_request():
    """
    Verify that a valid JWT is present in the request, and add
    the verified payload to the request context
    """

    token = get_token_auth_header()
    secret_key = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(token, secret_key, 'HS256')
    except (jwt.JWTClaimsError, jwt.JWTError):
        raise AuthError('Token is invalid', 401)

    _request_ctx_stack.top.current_user = payload


def requires_auth(optional: bool = False):
    """ A decorator to protect a Flask endpoint with JSON Web Tokens. """

    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except AuthError as e:
                if not optional:
                    raise e

            return f(*args, **kwargs)

        return decorator

    return wrapper


def requires_permission(required_permission: str) -> bool:
    """ In a protected endpoint, check if a specific permission exists in the current user """
    permissions = _request_ctx_stack.top.current_user['permissions']
    return required_permission in permissions


def generate_token(sub: str, permissions: list = []) -> str:
    """ Generate JWT token """
    payload = {
        'sub': sub,
        'exp': datetime.now() + timedelta(days=30),
        'permissions': permissions
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], 'HS256')
    return str(token)


def get_jwt_sub() -> str:
    """
    In a protected endpoint, this will return the user object for the JWT that is accessing the endpoint.
    If no JWT is present, ``None`` is returned.
    """
    if not hasattr(_request_ctx_stack.top, 'current_user'):
        return None
    else:
        return _request_ctx_stack.top.current_user['sub']
