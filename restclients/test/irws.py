import json
import logging
from django.test import TestCase, override_settings
from django.conf import settings
from restclients.irws import IRWS
from restclients.exceptions import InvalidIRWSName, DataFailureException, InvalidNetID
from restclients.exceptions import IRWSPersonNotFound, InvalidIRWSPerson
from restclients.dao_implementation.irws import File

logger = logging.getLogger(__name__)


@override_settings(RESTCLIENTS_IRWS_DAO_CLASS='restclients.dao_implementation.irws.File',
                   RESTCLIENTS_IRWS_SERVICE_NAME='registry-dev')
class IRWSTest(TestCase):
    def setUp(self):
        File._cache = {}

    def test_get_name_by_netid(self):
        irws = IRWS()
        name = irws.get_name_by_netid('javerage')
        self.assertEquals(name.display_cname, 'JAMES AVERAGE STUDENT')

    def test_put_name_by_netid(self):
        irws = IRWS()
        # prime the cache first
        irws.get_name_by_netid('javerage')

        response = irws.put_name_by_netid(
            'javerage',
            self._json_name_from_tuple(('J', '', 'Student')))
        self.assertEquals(200, response)
        name = irws.get_name_by_netid('javerage')
        self.assertEquals('J', name.display_fname)
        self.assertEquals('', name.display_mname)
        self.assertEquals('Student', name.display_lname)

    def test_put_name_by_netid_no_user(self):
        irws = IRWS()
        self.assertRaises(DataFailureException,
                          irws.put_name_by_netid,
                          'nonuser',
                          self._json_name_from_tuple(('J', '', 'Student')))

    def test_valid_name_part_good(self):
        irws = IRWS()
        self.assertTrue(irws.valid_name_part('james'))
        self.assertTrue(irws.valid_name_part(' '))
        self.assertTrue(irws.valid_name_part(' !$&\'*-,.?^_`{}~#+%'))

    def test_valid_name_part_bad(self):
        irws = IRWS()
        bad_chars = '"():;<>[\]|@'
        self.assertFalse(irws.valid_name_part(u'Jos\xe9'))  # utf-8
        for c in bad_chars:
            self.assertFalse(irws.valid_name_part(c),
                             "testing invalid character '{}'".format(c))

    def test_valid_name_part_too_long(self):
        # 64 is the magic number
        bad_name = 'a' * 65
        irws = IRWS()
        self.assertFalse(irws.valid_name_part(bad_name))
        # one less should be good
        self.assertTrue(irws.valid_name_part(bad_name[:-1]))

    def test_valid_irws_name_good(self):
        irws = IRWS()
        name = ('joe', 'average', 'user')
        names = irws.valid_irws_name_from_json(
           self. _json_name_from_tuple(name))
        self.assertEquals({'name'}, set(names.keys()))
        self.assertEquals(len(names['name']), 1)
        name = names['name'][0]
        self.assertEquals(name['display_fname'], 'joe')
        self.assertEquals(name['display_mname'], 'average')
        self.assertEquals(name['display_sname'], 'user')

    def test_valid_irws_name_empty_middle_name(self):
        irws = IRWS()
        name = ('joe', '', 'user')
        names = irws.valid_irws_name_from_json(
            self._json_name_from_tuple(name))
        self.assertEquals(names['name'][0]['display_mname'], '')

    def test_valid_irws_name_bad_json(self):
        irws = IRWS()
        bad_data_list = [
            ('{"display_fname": "joe", "display_mname": "average", '
             '"display_lname": "user"'),  # not terminated
            ('{"display_mname": "average", '
             '"display_lname": "user"}'),  # missing attribute
            ]

        for bad_data in bad_data_list:
            self.assertRaises(InvalidIRWSName,
                              irws.valid_irws_name_from_json,
                              bad_data)

    def test_valid_irws_name_required_fields_missing(self):
        irws = IRWS()
        bad_data_list = [
            ('', 'average', 'user'),
            ('joe', 'average', ''),
            ]

        for bad_data in bad_data_list:
            bad_json = self._json_name_from_tuple(bad_data)
            self.assertRaises(InvalidIRWSName,
                              irws.valid_irws_name_from_json,
                              bad_json)

    def test_valid_irws_name_bad_characters(self):
        irws = IRWS()
        bad_data_list = [
            ('@', 'average', 'user'),
            ('joe', '@', 'user'),
            ('joe', 'average', '@'),
            ]

        for bad_data in bad_data_list:
            bad_json = self._json_name_from_tuple(bad_data)
            self.assertRaises(InvalidIRWSName,
                              irws.valid_irws_name_from_json,
                              bad_json)

    def test_valid_irws_name_too_long(self):
        # 80 is the magic number
        irws = IRWS()
        bad_data_list = [
            ('f' * 30, 'm' * 30, 'l' * 19),
            ('f' * 40, '', 'l' * 40)]

        for bad_data in bad_data_list:
            # one less character will pass
            good_name = self._json_name_from_tuple(bad_data[0:2]
                                                   + (bad_data[2][:-1],))
            bad_name = self._json_name_from_tuple(bad_data)
            names = irws.valid_irws_name_from_json(good_name)
            # success
            self.assertTrue(names.get('name', None) is not None)
            # failure
            self.assertRaises(InvalidIRWSName,
                              irws.valid_irws_name_from_json,
                              bad_name)

    def test_get_identity_by_netid(self):
        irws = IRWS()
        identity = irws.get_identity_by_netid('javerage')
        self.assertNotEqual(0, len(identity.identifiers.keys()))

    def test_get_identity_by_netid_bad_netid(self):
        irws = IRWS()
        self.assertRaises(InvalidNetID,
                          irws.get_identity_by_netid,
                          'lkfajdslkjf#@$$@')

    def test_get_identity_by_netid_nonexistent(self):
        irws = IRWS()
        self.assertRaises(DataFailureException,
                          irws.get_identity_by_netid,
                          'nonuser')

    def test_get_hepps_person_by_netid(self):
        irws = IRWS()
        # idtest56 is set up to be a hepps person
        hepps_person = irws.get_hepps_person_by_netid('idtest56')
        self.assertEqual('N', hepps_person.wp_publish)
        self.assertEqual('28098ACBAC71425D9B2912757E4EF3AE', hepps_person.regid)

    def test_get_hepps_person_by_netid_not_hepps(self):
        irws = IRWS()
        # idtest55 is set up to NOT be a hepps person
        self.assertRaises(IRWSPersonNotFound,
                          irws.get_hepps_person_by_netid,
                          'idtest55')

    def test_post_hepps_person_by_netid(self):
        irws = IRWS()
        netid = 'idtest56'
        # prime the cache
        irws.get_hepps_person_by_netid(netid)
        response = irws.post_hepps_person_by_netid(
            netid,
            '{"wp_publish": "E"}')
        self.assertEqual(200, response)
        identity = irws.get_hepps_person_by_netid(netid)
        self.assertEqual('E', identity.wp_publish)

    def test_post_hepps_person_by_netid_not_hepps(self):
        irws = IRWS()
        self.assertRaises(IRWSPersonNotFound,
                          irws.post_hepps_person_by_netid,
                          'idtest55',
                          '{"wp_publish": "E"}')

    def test_post_hepps_person_by_netid_data_failure(self):
        self.assertRaises(DataFailureException,
                          IRWS().post_hepps_person_by_netid,
                          'idtest56',
                          '{"wp_publish": "E"}')

    def test_valid_hepps_person_from_json(self):
        person = IRWS().valid_hepps_person_from_json('{"wp_publish": "Y"}')
        expected = json.dumps({'person': [{'wp_publish': 'Y'}]})
        self.assertEqual(expected, json.dumps(person))
        # test all the possible values
        person = IRWS().valid_hepps_person_from_json('{"wp_publish": "N"}')
        person = IRWS().valid_hepps_person_from_json('{"wp_publish": "E"}')

    def test_valid_hepps_person_from_json_bad_payload(self):
        self.assertRaises(InvalidIRWSPerson,
                          IRWS().valid_hepps_person_from_json,
                          '{"wp_publish": "J"}')

    def test_valid_hepps_person_from_json_bad_json(self):
        self.assertRaises(InvalidIRWSPerson,
                          IRWS().valid_hepps_person_from_json,
                          '{"wp_publish":')

    def _json_name_from_tuple(self, x):
        return json.dumps({'display_fname': x[0],
                           'display_mname': x[1],
                           'display_lname': x[2]})
