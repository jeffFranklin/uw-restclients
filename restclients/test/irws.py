import json
from django.test import TestCase, override_settings
from django.conf import settings

from restclients.irws import IRWS
from restclients.exceptions import InvalidIRWSName

@override_settings(RESTCLIENTS_IRWS_DAO_CLASS='restclients.dao_implementation.irws.File',
                   RESTCLIENTS_IRWS_SERVICE_NAME='registry-dev')
class IRWSTest(TestCase):

    def test_get_name_by_netid(self):
        irws = IRWS()
        name = irws.get_name_by_netid('javerage')
        self.assertEquals(name.display_cname, 'JAMES AVERAGE STUDENT')

    def test_valid_name_part_good(self):
        irws = IRWS()
        self.assertTrue(irws.valid_name_part('james'))
        self.assertTrue(irws.valid_name_part(' '))

    def test_valid_name_part_bad(self):
        irws = IRWS()
        self.assertFalse(irws.valid_name_part('^'))
        self.assertFalse(irws.valid_name_part(u'Jos\xe9'))  # utf-8

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
            ('^', 'average', 'user'),
            ('joe', '^', 'user'),
            ('joe', 'average', '^'),
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
            ('012345678911234567892123456789',
             '312345678941234567895123456789',
             '6123456789712345678'),
            ('0123456789112345678921234567893123456789',
             '',
             '4123456789512345678961234567897123456789',
             )
            ]

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

    def _json_name_from_tuple(self, x):
        return json.dumps({'display_fname': x[0],
                           'display_mname': x[1],
                           'display_lname': x[2]})
