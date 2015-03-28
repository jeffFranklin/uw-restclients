"""
This is the interface for interacting with the UW Libraries Web Service.
"""

import logging
from restclients.digitlib import get_resource


url_prefix = "/php/currics/service.php?code="
sln_prefix = "&sln="
quarter_prefix = "&quarter="
year_prefix = "&year="
logger = logging.getLogger(__name__)


def get_subject_guide(course_code, sln, quarter, year):
    """
    :param sln: positive integer
    :param year: four digit number
    Return the string representing the url of
    the Library subject guide page
    """
    url = "%s%s%s%s%s%s%s%s" % (url_prefix,
                                course_code.replace(" ", "%20"),
                                sln_prefix, sln,
                                quarter_prefix, quarter,
                                year_prefix, year)
    return _extract_url(get_resource(url))


def _extract_url(data_in_resp):
    """
    :param data_in_resp: dict
    Return the string representing the url
    """
    if data_in_resp is not None:
        if data_in_resp.get("Location") is not None:
            return data_in_resp.get("Location")
        if data_in_resp.get("location") is not None:
            return data_in_resp.get("location")
    logger.warn("Invalid library curric response: %s" % data_in_resp)
    return None
