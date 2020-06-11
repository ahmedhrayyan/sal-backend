from os import environ
from .auth0 import Auth0

if ('AUTH0_DOMAIN') not in environ:
    raise ValueError('AUTH0_DOMAIN expected in environ')
domain = environ['AUTH0_DOMAIN']

def init_auth0():
    if ('CLIENT_ID' not in environ or 'CLIENT_SECRET' not in environ):
        raise ValueError('AUTH0_DOMAIN, CLIENT_ID and CLIENT_SECRET expected in environ')
    client_id = environ['CLIENT_ID']
    client_secret = environ['CLIENT_SECRET']
    auth0 = Auth0(domain, client_id, client_secret)
    return auth0
