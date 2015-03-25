from django.test import TestCase, override_settings
from django.conf import settings

from restclients.irws import IRWS

@override_settings(RESTCLIENTS_IRWS_DAO_CLASS='restclients.dao_implementation.irws.File',
                   RESTCLIENTS_IRWS_SERVICE_NAME='registry-dev')
class IRWSTest(TestCase):

    def test_irws(self):
        irws = IRWS()
        name = irws.get_name_by_netid('javerage')
        self.assertEquals(name.display_cname, 'JAMES AVERAGE STUDENT')
