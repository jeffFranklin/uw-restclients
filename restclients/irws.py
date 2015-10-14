"""
This is the interface for interacting with the Identity Registry Web Service.
"""

import re
import copy
import json
import logging
from django.conf import settings
from restclients.dao import IRWS_DAO
from restclients.exceptions import InvalidRegID, InvalidNetID, InvalidEmployeeID
from restclients.exceptions import InvalidIdCardPhotoSize
from restclients.exceptions import DataFailureException
from restclients.exceptions import InvalidIRWSName, InvalidIRWSPerson, IRWSPersonNotFound
from restclients.models.irws import Name, UwhrPerson, PersonIdentity
from StringIO import StringIO
from urllib import urlencode

logger = logging.getLogger(__name__)


class IRWS(object):
    """
    The IRWS object has methods for getting person information.
    """
    def __init__(self, actas=None):
        self.actas = actas
        self._re_regid = re.compile(r'^[A-F0-9]{32}$', re.I)
        self._re_personal_netid = re.compile(r'^[a-z][a-z0-9]{0,7}$', re.I)
        self._re_admin_netid = re.compile(r'^[a-z]adm_[a-z][a-z0-9]{0,7}$', re.I)
        self._re_application_netid = re.compile(r'^a_[a-z0-9\-\_\.$.]{1,18}$', re.I)
        self._re_employee_id = re.compile(r'^\d{9}$')
        """ Consider adding back +, #, and % when irws stops decoding """
        self._re_name_part = re.compile(r'^[\w !$&\'*\-,.?^_`{}~#+%]*$')
        self._service_name = settings.RESTCLIENTS_IRWS_SERVICE_NAME

    def get_identity_by_netid(self, netid):
        """
        Returns a restclients.irws.PersonIdentity object for the given netid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        if not self.valid_uwnetid(netid):
            raise InvalidNetID(netid)
        dao = IRWS_DAO()
        url = "/%s/v1/person?uwnetid=%s" % (self._service_name, netid.lower())
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._identity_from_json(response.data)

    def get_name_by_netid(self, netid):
        """
        Returns a restclients.irws.Name object for the given netid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        if not self.valid_uwnetid(netid):
            raise InvalidNetID(netid)

        dao = IRWS_DAO()
        url = "/%s/v1/name/uwnetid=%s" % (self._service_name, netid.lower())
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._name_from_json(response.data)

    def put_name_by_netid(self, netid, data):
        """
        Updates display info for a Name object
        """
        if not self.valid_uwnetid(netid):
            raise InvalidNetID(netid)

        pd = self.valid_irws_name_from_json(data)
        dao = IRWS_DAO()
        url = "/%s/v1/name/uwnetid=%s" % (self._service_name, netid.lower())
        response = dao.putURL(url, {"Accept": "application/json"}, json.dumps(pd))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def get_hr_person_by_uri(self, uri):
        """
        Returns a restclients.irws.UwhrPerson object for the given uri (from identity).
        If the record id isn't found, nothing will be returned. If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        url = "/%s/v1%s" % (self._service_name, uri)
        response = IRWS_DAO().getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._hr_person_from_json(response.data)

    def get_hepps_person_by_netid(self, netid):
        """
        Deprecated. Replace with get_hr_person_by_netid.
        """
        logger.info('Using depecrated method get_hepps_person_by_netid')
        return self.get_hr_person_by_netid(netid)

    def get_hr_person_by_netid(self, netid):
        """
        Returns a restclients.irws.UwhrPerson object for a given netid. Two round
        trips - one to get the identity, and a second to look up a person based on
        the 'hepps' or 'uwhr' uri in the payload
        """
        identity = self.get_identity_by_netid(netid)
        if not {'hepps', 'uwhr'} & set(identity.identifiers.keys()):
            raise IRWSPersonNotFound('netid ' + netid + ' not a hepps/uwhr person')
        source = 'uwhr' if 'uwhr' in identity.identifiers.keys() else 'hepps'
        return self.get_hr_person_by_uri(identity.identifiers[source])

    def post_hepps_person_by_netid(self, netid):
        """
        Deprecated. Replace with post_hr_person_by_netid.
        """
        logger.info('Using depecrated method post_hepps_person_by_netid')
        return self.post_hr_person_by_netid(netid)

    def post_hr_person_by_netid(self, netid, data):
        """
        Post to the irws person hr resource.
        We look up the person by netid to get the uri to post to.
        """
        if not self.valid_uwnetid(netid):
            raise InvalidNetID(netid)
        hepps_person = self.valid_hr_person_from_json(data)
        identity = self.get_identity_by_netid(netid)
        if not {'hepps', 'uwhr'} & set(identity.identifiers.keys()):
            raise IRWSPersonNotFound('netid ' + netid + ' not a hepps/uwhr person')
        source = 'uwhr' if 'uwhr' in identity.identifiers.keys() else 'hepps'
        post_url = '/{}/v1{}'.format(self._service_name,
                                      identity.identifiers[source])
        response = IRWS_DAO().postURL(post_url,
                               {'Accept': 'application/json'},
                               json.dumps(hepps_person))
        if response.status != 200:
            raise DataFailureException(post_url, response.status, response.data)

        return response.status

    def valid_uwnetid(self, netid):
        uwnetid = str(netid)
        return (self._re_personal_netid.match(uwnetid) != None
                or self._re_admin_netid.match(uwnetid) != None
                or self._re_application_netid.match(uwnetid) != None)

    def valid_uwregid(self, regid):
        return True if self._re_regid.match(str(regid)) else False

    def valid_employee_id(self, employee_id):
        return True if self._re_employee_id.match(str(employee_id)) else False

    def valid_irws_name_from_json(self, data):
        # construct and validate the put data
        putname = {}
        try:
            dataname = json.loads(data)
            putname['display_fname'] = dataname['display_fname']
            putname['display_mname'] = dataname['display_mname']
            putname['display_sname'] = dataname['display_lname']
        except:
            raise InvalidIRWSName('invalid json')

        if any(not self.valid_name_part(x) for x in putname.values()):
            raise InvalidIRWSName('name too long or has invalid characters')
        if any(putname[x] == '' for x in ('display_fname', 'display_sname')):
            raise InvalidIRWSName('required fields cannot be empty')
        if len(' '.join(x for x in putname.values() if x != '')) > 80:
            raise InvalidIRWSName(
                'complete display name cannot be longer than 80 characters')

        pd = {}
        pd['name'] = []
        pd['name'].append(putname)

        return pd

    def valid_hr_person_from_json(self, data):
        """
        Validate input of supported fields and return an
        object that can be posted to irws
        """
        post_person = {}
        try:
            data_person = json.loads(data)
            post_person['wp_publish'] = data_person.pop('wp_publish')
            if len(data_person.keys()) != 0:
                logger.info('ignoring the following keys for post: {}'.format(
                        ', '.join(data_person.keys())))
        except:
            raise InvalidIRWSPerson('invalid json')

        if post_person['wp_publish'] not in ('Y', 'N', 'E'):
            raise InvalidIRWSPerson('wp_publish can only be Y, N, or E')

        return {'person': [post_person]}

    def valid_name_part(self, name):
        return (len(name) <= 64 and
                self._re_name_part.match(name) != None)

    def _hr_person_from_json(self, data):
        """
        Internal method, for creating the UwhrPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = UwhrPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        if 'studentid' in person_data: person.studentid = person_data['studentid']

        person.fname = person_data['fname']
        person.lname = person_data['lname']

        person.category_code = person_data['category_code']
        person.category_name = person_data['category_name']
        
        if 'wp_publish' in person_data: person.wp_publish = person_data['wp_publish']
        else: person.wp_publish = 'N'  # default to no
        return person

    def _name_from_json(self, data):
        nd = json.loads(data)['name'][0]
        name = Name()
        name.validid = nd['validid']
        if 'formal_cname' in nd: name.formal_cname = nd['formal_cname']
        if 'formal_fname' in nd: name.formal_fname = nd['formal_fname']
        if 'formal_sname' in nd: name.formal_lname = nd['formal_sname']
        if 'formal_privacy' in nd: name.formal_privacy = nd['formal_privacy']
        if 'display_cname' in nd: name.display_cname = nd['display_cname']
        if 'display_fname' in nd: name.display_fname = nd['display_fname']
        if 'display_mname' in nd: name.display_mname = nd['display_mname']
        if 'display_sname' in nd: name.display_lname = nd['display_sname']
        if 'display_privacy' in nd: name.display_privacy = nd['display_privacy']
        return name

    def _identity_from_json(self, data):
        persj = json.loads(data)['person'][0]
        idj = persj['identity']
        ident = PersonIdentity()
        ident.regid = idj['regid']
        ident.identifiers = copy.deepcopy(idj['identifiers'])
        return ident

