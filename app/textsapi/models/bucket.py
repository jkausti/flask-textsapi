from pynamodb.models import Model

from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    UTCDateTimeAttribute,
    BooleanAttribute
)

import os

def table_name():
    return 'textapi-{}'.format(os.getenv('BOILERPLATE_ENV', 'dev'))


class Bucket(Model):

    class Meta:
        table_name = table_name()
        region = 'eu-central-1'

    username = UnicodeAttribute(hash_key=True)
    sort = UnicodeAttribute(range_key=True) # Composite key of 'BUCKET_'+public_id
    bucket_name = UnicodeAttribute()
    created_date = UTCDateTimeAttribute()
    public_id = NumberAttribute()
    full = BooleanAttribute(default=False)

    def __repr__(self):
        return "Bucket full: {}".format(self.full)
