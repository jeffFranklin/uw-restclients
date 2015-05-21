"""
Contains IRWS DAO implementations.
"""

from django.conf import settings
from restclients.mock_http import MockHTTP
import re
import logging
import json
from restclients.dao_implementation.live import get_con_pool, get_live_url
from restclients.dao_implementation.mock import get_mockdata_url

logger = logging.getLogger(__name__)

# This seemed like a good number based on a test using a class w/ 300 students.
# The range 10-50 all did well, so this seemed like the most sociable, high performing
# number to choose
IRWS_MAX_POOL_SIZE = 10

class File(object):
    """
    The File DAO implementation returns generally static content.  Use this
    DAO with this configuration:

    RESTCLIENTS_IRWS_DAO_CLASS = 'restclients.dao_implementation.irws.File'
    """
    # cache of results to fake puts and posts in memory
    _cache = {}

    def getURL(self, url, headers):
        if url in File._cache:
            response = MockHTTP()
            response.status = 200
            response.data = File._cache[url]
            response.headers = {'Content-Type': 'application/json'}
        else:
            response = get_mockdata_url("irws", "file", url, headers)
            File._cache[url] = response.data
        return response

    def putURL(self, url, headers, body):
        response = MockHTTP()
        logger.debug('made it to putURL')

        response.headers = {"Content-Type": 'application/json'}
        if url in File._cache:
            cache = json.loads(File._cache[url])
            request = json.loads(body)
            type = request.keys()[0]
            for attr in request[type][0].keys():
                cache[type][0][attr] = request[type][0][attr]
            File._cache[url] = json.dumps(cache)
            response.data = File._cache[url]
            response.status = 200
        else:
            response.data = body
            response.status = 404
        return response

    def postURL(self, url, headers, body):
        return self.putURL(url, headers, body)


class AlwaysJAverage(object):
    """
    This DAO ensures that all users have javerage's regid
    """
    def getURL(self, url, headers):
        real = File()

        if re.search('/identity/v1/person/([\w]+).json', url):
            return real.getURL('/identity/v1/person/javerage.json', headers)

        return real.getURL(url, headers)


class ETag(object):
    """
    The ETag DAO is a testing DAO, that is just here for
    testing the ETag cache class.  You don't want to use it
    for anything else.
    """
    def getURL(self, url, headers):
        if "If-None-Match" in headers and url == "/same":
            response = MockHTTP()
            response.status = 304
            return response

        else:
            response = MockHTTP()
            response.status = 200
            response.data = "Body Content"
            response.headers = {"ETag": "A123BBB"}

            return response


class Live(object):
    """
    This DAO provides real data.  It requires further configuration, e.g.

    RESTCLIENTS_IRWS_CERT_FILE='/path/to/an/authorized/cert.cert',
    RESTCLIENTS_IRWS_KEY_FILE='/path/to/the/certs_key.key',
    RESTCLIENTS_IRWS_HOST='https://ucswseval1.cac.washington.edu:443',
    """
    def getURL(self, url, headers):
        return get_live_url(self.pool, 'GET',
                            settings.RESTCLIENTS_IRWS_HOST,
                            url, headers=headers,
                            service_name='irws')

    def putURL(self, url, headers, body):
        return get_live_url(self.pool, 'PUT',
                            settings.RESTCLIENTS_IRWS_HOST,
                            url, headers=headers, body=body,
                            service_name='irws')

    def postURL(self, url, headers, body):
        return get_live_url(self.pool, 'POST',
                            settings.RESTCLIENTS_IRWS_HOST,
                            url, headers=headers, body=body,
                            service_name='irws')

    _pool = None
    @property
    def pool(self):
        if Live._pool is None:
            Live._pool = get_con_pool(settings.RESTCLIENTS_IRWS_HOST,
                                 settings.RESTCLIENTS_IRWS_KEY_FILE,
                                 settings.RESTCLIENTS_IRWS_CERT_FILE,
                                 max_pool_size=IRWS_MAX_POOL_SIZE)
        return Live._pool

