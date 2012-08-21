"""
This is the interface for interacting with the Person Web Service.
"""

from restclients.dao import PWS_DAO
from restclients.exceptions import InvalidRegID, InvalidNetID, DataFailureException
from restclients.models import Person
import json
import re


class PWS(object):
    """
    The PWS object has methods for getting person information.
    """

    def get_person_by_regid(self, regid):
        if not re.match(r'^[A-F0-9]{32}$', regid, re.I):
            raise InvalidRegID(regid)

        dao = PWS_DAO()
        url = "/identity/v1/person/%s.json" % regid.upper()
        response = dao.getURL(url, { "Accept":"application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.read())

        person_data = json.loads(response.data)
        person = Person()
        person.uwnetid = person_data["UWNetID"]
        person.uwregid = person_data["UWRegID"]

        return person


    def get_person_by_netid(self, netid):
        if not re.match(r'^([a-z]adm_)?[a-z][a-z0-9]{0,7}$', netid, re.I):
            raise InvalidNetID(netid)

        # ... fill out the person model

