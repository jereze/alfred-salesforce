#!/usr/bin/env python3
# encoding: utf-8

from urllib.parse import urlencode
from workflow.web import get, post


BASE_AUTH_URL = "https://login.salesforce.com/services/oauth2/authorize"
REFRESH_TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"
CLIENT_ID = "3MVG9HxRZv05HarTt_Zg0T5Tpx50bblr71abxsEHwHDXhJqGQ406d6oH6UTNDNGpS4QaqrYt0RBbLBomvhbwa"


def get_oauth_url():
    params = {
        'redirect_uri': 'http://localhost:2576/',
        'client_id': CLIENT_ID,
        'response_type': 'token'
    }
    return '%s?%s' % (BASE_AUTH_URL, urlencode(params))


class Salesforce(object):
    def __init__(self, wf=None, access_token=None, refresh_token=None, instance_url=0):
        self.wf = wf
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.instance_url = instance_url

    def api_call(self, action, parameters = {}, method = 'get', data = {}, _count = 0):
        """
        Helper function to make calls to Salesforce REST API.
        """
        headers = {
            'Content-type': 'application/json',
            'Accept-Encoding': 'gzip',
            'Authorization': 'Bearer %s' % self.access_token
        }
        if method == 'get':
            r = get(self.instance_url+action, headers=headers, params=parameters, timeout=5)
        elif method == 'post':
            r = post(self.instance_url+action, headers=headers, data=data, params=parameters, timeout=5)
        else:
            raise ValueError('Method should be get or post.')
        self.wf.logger.info('API %s call: %s' % (method, r.url) )
        if r.status_code == 401 and _count < 1:
            self.refresh_access_token()
            return self.api_call(action, parameters, method, data, _count+1)
        if ((r.status_code == 200 and method == 'get') or (r.status_code == 201 and method == 'post')):
            return r.json()
        else:
            self.wf.logger.debug(r.text)
            raise ValueError('API error when calling %s (%i): %s' % (r.url, r.status_code, r.text))

    def save_new_access_token(self, access_token):
        """
        Function to save the access_token. Requires a wf object to save permanently.
        """
        self.access_token = access_token
        if self.wf is not None:
            self.wf.save_password('access_token', access_token)

    def refresh_access_token(self):
        """
        OAuth Refresh Token Process
        """
        r = post(REFRESH_TOKEN_URL, timeout=5, data={
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": CLIENT_ID,
            "format": "json"
        })
        self.wf.logger.info(self.refresh_token)
        self.wf.logger.info('API %s call: %s' % ('post', r.url) )
        if r.status_code < 300 and "access_token" in list(r.json().keys()):
            self.save_new_access_token(r.json().get("access_token"))
            self.wf.logger.info('New access token saved.')
        else:
            self.wf.logger.debug(r.text)
            raise ValueError('API error when refreshing the token (%i): %s' % (r.status_code, r.text))


    def search_call(self, term):
        r = self.api_call('/services/data/v40.0/search/', parameters={
            'q': "FIND {%s} IN ALL FIELDS RETURNING Account (Id, Name), Contact (Id, Name), Opportunity (Id, Name), Lead (Id, Name) WITH METADATA='LABELS' " % term
        })

