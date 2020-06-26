from os import environ
import json
from six.moves.urllib.request import urlopen
from functools import wraps
from jose import jwt
from .auth0 import Auth0, Auth0Error
from flask import request, _request_ctx_stack

domain = 'sal22.eu.auth0.com'
api_audience = 'https://sal.com/'
algorithms = ["RS256"]

# Auth0 management api (manipulate auth0 data)


def init_auth0():
    if ('CLIENT_ID' not in environ or 'CLIENT_SECRET' not in environ):
        raise ValueError(
            'CLIENT_ID and CLIENT_SECRET expected in environ')
    client_id = environ['CLIENT_ID']
    client_secret = environ['CLIENT_SECRET']
    auth0 = Auth0(domain, client_id, client_secret)
    return auth0

# Authentication and Authorization
# See: https://auth0.com/docs/quickstart/backend/python/01-authorization

# Error handler


class AuthError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({
            "code": "authorization_header_missing",
            "description": "Authorization header is expected"
        }, 401)
    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthError({
            "code": "invalid_header",
            "description": "Authorization header must start with Bearer"
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            "code": "invalid_header",
            "description": "Token not found"
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            "code": "invalid_header",
            "description":
            "Authorization header must be Bearer token"
        }, 401)
    token = parts[1]
    return token


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+domain+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=algorithms,
                    audience=api_audience,
                    issuer="https://"+domain+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({
                    "code": "token_expired",
                    "description": "token is expired"
                }, 401)
            except jwt.JWTClaimsError:
                raise AuthError({
                    "code": "invalid_claims",
                    "description":
                    "incorrect claims, please check the audience and issuer"
                }, 401)
            except Exception:
                raise AuthError({
                    "code": "invalid_header",
                    "description": "Unable to parse authentication token."
                }, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({
            "code": "invalid_header",
            "description": "Unable to find appropriate key"
        }, 401)
    return decorated


def requires_permission(required_permission):
    permissions = _request_ctx_stack.top.current_user['permissions']
    for permission in permissions:
        if permission == required_permission:
            return True
    return False
