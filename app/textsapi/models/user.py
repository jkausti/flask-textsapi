from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from werkzeug.security import generate_password_hash, check_password_hash

from ..models.blacklist import BlacklistedToken
from ..config import key

import jwt
import datetime
import os
import traceback


def table_name():
    return 'textapi-{}'.format(os.getenv('BOILERPLATE_ENV', 'dev'))


class User(Model):
    
    class Meta:
        table_name = table_name()
        region = 'eu-central-1'

    username = UnicodeAttribute(hash_key=True)
    sort = UnicodeAttribute(range_key=True)
    email = UnicodeAttribute()
    password_hash = UnicodeAttribute()
    registered_on = UTCDateTimeAttribute()
    public_id = NumberAttribute()

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def encode_auth_token(self, username, user_type):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': username,
                'user_type': user_type
            }
            return jwt.encode(
                payload,
                key,
                algorithm='HS256'
            )
        except Exception as e:
            return e
    
    @staticmethod
    def decode_auth_token(token):
        try:
            payload = jwt.decode(token, key=key)
            is_blacklisted_token = BlacklistedToken.check_blacklist(token)
            if is_blacklisted_token:
                return ('ERROR', 'Token not valid. Please log in again.')
            else:
                return payload
        except jwt.ExpiredSignatureError:
            return ('ERROR', 'Signature expired. Please obtain new token.')
        except jwt.InvalidTokenError:
            return ('ERROR', 'Invalid token. Please obtain new token.')
        except Exception as e:
            traceback.print_exc()
            return ('ERROR', e)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User '{}'>".format(self.username)
    
    # def _table_name(self, name):
    #     return 'textapi-{}'.format(name)