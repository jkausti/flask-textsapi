from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, NumberAttribute

import os


def table_name():
    return 'textapi-{}'.format(os.getenv('BOILERPLATE_ENV', 'dev'))

class Text(Model):

    class Meta:
        table_name = table_name()
        region = 'eu-central-1'
    
    username = UnicodeAttribute(hash_key=True)
    sort = UnicodeAttribute(range_key=True)
    bucket_id = NumberAttribute()
    raw_text_path = UnicodeAttribute()
    preprocessed_text_path = UnicodeAttribute(null=True)
    processed_text_path = UnicodeAttribute(null=True)
    processing_complete = BooleanAttribute(default=False)
    submission_id = NumberAttribute()
    public_id = NumberAttribute()


    def __repr__(self):
        return "Processed: {}".format(self.processing_complete)