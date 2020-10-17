from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute

import os


def table_name():
    return 'textapi-{}'.format(os.getenv('BOILERPLATE_ENV', 'dev'))


class BlacklistedToken(Model):

    class Meta:
        table_name = table_name()
        region = 'eu-central-1'

    username = UnicodeAttribute(hash_key=True)
    sort = UnicodeAttribute(range_key=True) #TOKEN_001 etc.
    token = UnicodeAttribute()
    blacklisted_on = UTCDateTimeAttribute()

    def __repr__(self):
        return "token: {}".format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether token has been blacklisted
        condition = BlacklistedToken.token == auth_token
        try:
            res = [x for x in BlacklistedToken.scan(filter_condition=condition)][0]
            if res:
                return True
            else:
                return False
        except IndexError:
            return False
        except Exception:
            return False
