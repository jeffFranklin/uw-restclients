import pickle
from django.db import models
from django.template import Context, loader
from base64 import b64encode, b64decode
from datetime import datetime
from restclients.util.date_formator import abbr_week_month_day_str
from restclients.exceptions import InvalidCanvasIndependentStudyCourse
from restclients.exceptions import InvalidCanvasSection


# IRWS Person Identity
class PersonIdentity(models.Model):
    regid = models.CharField(max_length=32)

    def __init__(self, *args, **kwargs):
        super(PersonIdentity, self).__init__(*args, **kwargs)
        self.identifiers = {}

    
# IRWS Name
class Name(models.Model):
    validid = models.CharField(max_length=32, unique=True)
    formal_cname = models.CharField(max_length=255)
    formal_fname = models.CharField(max_length=255)
    formal_lname = models.CharField(max_length=255)
    formal_privacy = models.CharField(max_length=32)
    display_cname = models.CharField(max_length=255)
    display_fname = models.CharField(max_length=255)
    display_mname = models.CharField(max_length=255)
    display_lname = models.CharField(max_length=255)
    display_privacy = models.CharField(max_length=32)


    def json_data(self):
        return {"formal_cname": self.formal_cname,
                "formal_fname": self.formal_fname,
                "formal_lname": self.formal_lname,
                "formal_privacy": self.formal_privacy,
                "display_cname": self.display_cname,
                "display_fname": self.display_fname,
                "display_mname": self.display_mname,
                "display_lname": self.display_lname,
                "display_privacy": self.display_privacy,
                }

    def __eq__(self, other):
        return self.uwregid == other.uwregid

    class Meta:
        app_label = "restclients"


# IRWS Uwhr Person
class UwhrPerson(models.Model):
    validid = models.CharField(max_length=32, unique=True)
    regid = models.CharField(max_length=32,
                               db_index=True,
                               unique=True)
    studentid = models.CharField(max_length=32)


    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    category_code = models.CharField(max_length=4)
    category_name = models.CharField(max_length=4)

    wp_name = models.CharField(max_length=255)
    wp_department = models.CharField(max_length=255)
    wp_email = models.CharField(max_length=255)
    wp_email_2 = models.CharField(max_length=255)
    wp_phone = models.CharField(max_length=32)
    wp_title = models.CharField(max_length=255)
    wp_address = models.CharField(max_length=255)
    wp_name = models.CharField(max_length=255)
    wp_publish = models.NullBooleanField()

    college = models.CharField(max_length=255)
    department = models.CharField(max_length=250)
    home_department = models.CharField(max_length=250)
    mailstop = models.CharField(max_length=250)
    unit = models.CharField(max_length=250)

    hepps_type = models.CharField(max_length=2)
    hepps_status = models.CharField(max_length=2)

    budget = models.CharField(max_length=24)
    faccode = models.CharField(max_length=24)
    source_code = models.CharField(max_length=2)
    source_name = models.CharField(max_length=32)
    status_code = models.CharField(max_length=2)
    status_name = models.CharField(max_length=32)

    in_feed = models.CharField(max_length=2)

    created = models.CharField(max_length=250)
    updated = models.CharField(max_length=250)

    def json_data(self):
        return {'uwnetid': self.uwnetid,
                'uwregid': self.uwregid,
                'first_name': self.first_name,
                'surname': self.surname,
                'full_name': self.full_name,
                'whitepages_publish': self.whitepages_publish,
                'email1': self.email1,
                'email2': self.email2,
                'phone1': self.phone1,
                'phone2': self.phone2,
                'title1': self.title1,
                'title2': self.title2,
                'voicemail': self.voicemail,
                'fax': self.fax,
                'touchdial': self.touchdial,
                'address1': self.address1,
                'address2': self.address2,
                'mailstop': self.mailstop,
                }

    def __eq__(self, other):
        return self.uwregid == other.uwregid

    class Meta:
        app_label = "restclients"


