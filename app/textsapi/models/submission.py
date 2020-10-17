from pynamodb.models import Model

from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    JSONAttribute,
    BooleanAttribute,
    UTCDateTimeAttribute,
    ListAttribute
)

import os

def table_name():
    return 'textapi-{}'.format(os.getenv('BOILERPLATE_ENV', 'dev'))


class Submission(Model):

    class Meta:
        table_name = table_name()
        region = 'eu-central-1'
    
    username = UnicodeAttribute(hash_key=True)
    sort = UnicodeAttribute(range_key=True) #use format of 'SUBMISSION_001', 'SUBMISSION_002' etc.
    text_count = NumberAttribute()
    submitted_date = UTCDateTimeAttribute()
    tags = ListAttribute(null=True)
    public_id = NumberAttribute()

    
    def __repr__(self):
        return "Texts: {}".format(self.text_count)

