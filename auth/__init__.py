from functools import wraps
from flask import request, _request_ctx_stack
from jose import jwt
from datetime import datetime, timedelta
from db.models import Role

class AuthError(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code


def get_token_auth_header() -> str:
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


def requires_auth(secret_key):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = jwt.decode(token, secret_key, 'HS256')
            except (jwt.JWTClaimsError, jwt.ExpiredSignatureError):
                raise AuthError('Token is invalid', 401)

            _request_ctx_stack.top.curr_user = payload
            return f(*args, **kwargs)
        return decorated
    return decorator


def requires_permission(required_permission) -> bool:
    permissions = _request_ctx_stack.top.curr_user['permissions']
    return required_permission in permissions


def gen_token(secret_key, user) -> str:
    permissions = Role.query.get(user.role_id).permissions
    payload = {
        'sub': user.username,
        'exp': datetime.now() + timedelta(days=30),
        'permissions': [permission.name for permission in permissions]
    }
    token = jwt.encode(payload, secret_key, 'HS256')
    return str(token)
