from ..models.user import User
from .blacklist_service import save_token

from pynamodb.exceptions import DoesNotExist

from ..config import key

import traceback
import jwt


class Auth:

    @staticmethod
    def obtain_user_token(data):
        try:
            user = User.get(hash_key=data['username'], range_key='customer')
            if user and user.verify_password(data['password']):
                auth_token = user.encode_auth_token(user.username, user.sort)
                if auth_token:
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully obtained token.',
                        'authorization': auth_token.decode()
                    }

                    return response_object, 200
            else:
                response_object = {
                    'status': 'failed',
                    'message': 'username or password does not match'
                }
                return response_object, 401
        except DoesNotExist:
            traceback.print_exc()
            response_object = {
                'status': 'failed',
                'message': 'username or password does not match'
            }
            return response_object, 401
        except Exception:
            traceback.print_exc()
            response_object = {
                'status': 'failed',
                'message': 'Application error. Contact system owner.'
            }
            return response_object, 500

    @staticmethod
    def destroy_user_token(data):
        if data:
            auth_token = data.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, str):
                return save_token(token=auth_token, username=resp)
            else:
                response_object = {
                    'status': 'failed',
                    'message': resp
                }
                return response_object, 401
        else:
            response_object = {
                'status': 'failed',
                'message': 'Provide a valid auth token'
            }
            return response_object, 403

    @staticmethod
    def get_logged_in_user(new_request):
        auth_token = new_request.headers.get('Authorization')
        if auth_token:
            try:
                try:
                    payload = User.decode_auth_token(auth_token.split(' ')[1])
                    username = payload['sub']
                    user_type = payload['user_type']
                except TypeError:
                    response_object = {
                        'status': 'failed',
                        'message': 'Could not authenticate user.'
                    }
                    return response_object, 404
                if isinstance(username, str):
                    user = User.get(hash_key=username, range_key=user_type)
                    response_object = {
                        'status': 'success',
                        'data': {
                            'username': user.username,
                            'type': user.sort,
                            'email': user.email,
                            'registered_on': str(user.registered_on),
                            'public_id': user.public_id
                        }
                    }
                    return response_object, 200
                else:
                    response_object = {
                        'status': 'failed',
                        'message': username[1]
                    }
                    return response_object, 401
            except Exception as e:
                traceback.print_exc()
                return {
                    'status': 'failed',
                    'message': 'Could not authenticate user.'
                }, 500
        else:
            response_object = {
                'status': 'failed',
                'message': 'Provide a valid auth-token'
            }
            return response_object, 401

    @staticmethod
    def obtain_root_token(data):
        try:
            user = User.get(hash_key=data['username'], range_key='root_admin')
            if user and user.verify_password(data['password']):
                auth_token = user.encode_auth_token(user.username, user.sort)
                if auth_token:
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully obtained token.',
                        'Authorization': auth_token.decode()
                    }

                    return response_object, 200
            else:
                response_object = {
                    'status': 'failed',
                    'message': 'username or password does not match'
                }
                return response_object, 401
        except DoesNotExist:
            traceback.print_exc()
            response_object = {
                'status': 'failed',
                'message': 'username or password does not match'
            }
            return response_object, 401
        except Exception:
            traceback.print_exc()
            response_object = {
                'status': 'failed',
                'message': 'Application error. Contact system owner.'
            }
            return response_object, 500

    @staticmethod
    def obtain_admin_token(data):
        try:
            user = User.get(hash_key=data['username'], range_key='admin')
            if user and user.verify_password(data['password']):
                auth_token = user.encode_auth_token(user.username, user.sort)
                if auth_token:
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully obtained token.',
                        'Authorization': auth_token.decode()
                    }

                    return response_object, 200
            else:
                response_object = {
                    'status': 'failed',
                    'message': 'username or password does not match'
                }
                return response_object, 401
        except DoesNotExist:
            traceback.print_exc()
            response_object = {
                'status': 'failed',
                'message': 'username or password does not match'
            }
            return response_object, 401
        except Exception:
            traceback.print_exc()
            response_object = {
                'status': 'failed',
                'message': 'Application error. Contact system owner.'
            }
            return response_object, 500
