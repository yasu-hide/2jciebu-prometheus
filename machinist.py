#!/usr/bin/env python
import sys, json
if sys.version_info.major != 2:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
else:
    from urllib2 import urlopen, Request, HTTPError
    from urllib import urlencode
    from urlparse import urlparse
from contextlib import closing

class Machinist:
    ENDPOINT_URL = 'https://gw.machinist.iij.jp/endpoint'

    def __init__(self, api_key):
        self.api_key = api_key
    def set_latest(self, req_data={}):
        req_header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key
        }
        req = Request(self.ENDPOINT_URL, data=json.dumps(req_data).encode(), headers=req_header)
        with closing(urlopen(req)) as res:
            rcode = res.getcode()
            body = res.read()
            if body:
                body = body.decode()
            if rcode == 200:
                return json.loads(body)
        return {}