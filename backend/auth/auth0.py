import http.client
import json

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
        conn.request('POST', '/oauth/token', json.dumps(payload), headers)
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
