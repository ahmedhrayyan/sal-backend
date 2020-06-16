import http.client
import json

# Error handler


class Auth0Error(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


class Auth0:
    def __init__(self, domain, client_id, client_secret):
        self.domain = domain
        conn = http.client.HTTPSConnection(domain)
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': 'https://{}/api/v2/'.format(domain),
            'grant_type': 'client_credentials'
        }
        headers = {
            'content-type': 'application/json'
        }
        try:
            conn.request('POST', '/oauth/token', json.dumps(payload), headers)
        except Exception:
            raise Auth0Error('Error initializing auth0 connection', 500)
        res = conn.getresponse()
        data = json.loads(res.read())
        self.access_token = data['access_token']

    def get_user(self, id, fields=None):
        conn = http.client.HTTPSConnection(self.domain)
        headers = {
            'content-type': "application/json",
            'authorization': "Bearer {}".format(self.access_token)
        }
        url = '/api/v2/users/{}'.format(id)
        if fields is not None:
            url += '?fields={}'.format(','.join(fields))
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data)
