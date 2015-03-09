"""
Contains IRWS DAO implementations.
"""

from django.conf import settings
from restclients.mock_http import MockHTTP
import re
from restclients.dao_implementation.live import get_con_pool, get_live_url
from restclients.dao_implementation.mock import get_mockdata_url

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
    def getURL(self, url, headers):
        return get_mockdata_url("irws", "file", url, headers)

    def putURL(self, url, headers, body):
        response = MockHTTP()

        if "If-Match" in headers:
            response.status = 200  # update
        else:
            response.status = 201  # create
        response.headers = {"X-Data-Source": "GWS file mock data",
                            "Content-Type": headers["Content-Type"]}
        response.data = body
        return response


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
    pool = None

    def getURL(self, url, headers):
        if Live.pool == None:
            Live.pool = get_con_pool(settings.RESTCLIENTS_IRWS_HOST,
                                     settings.RESTCLIENTS_IRWS_KEY_FILE,
                                     settings.RESTCLIENTS_IRWS_CERT_FILE,
                                     max_pool_size= IRWS_MAX_POOL_SIZE)
        return get_live_url(Live.pool, 'GET',
                            settings.RESTCLIENTS_IRWS_HOST,
                            url, headers=headers,
                            service_name='irws')

