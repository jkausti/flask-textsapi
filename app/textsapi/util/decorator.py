from functools import wraps
from flask import request

from ..service.auth_helper import Auth


def token_required(f):
    wraps(f)
    def decorated(*args, **kwargs):
        data, status = Auth.get_logged_in_user(request)
        token = data.get('data')

        if not token:
            return data, status

        return f(*args, **kwargs)
    
    return decorated

def admin_token_required(f):
    wraps(f)
    def decorated(*args, **kwargs):

        data, status = Auth.get_logged_in_user(request)
        token = data.get('data')

        if not token:
            return data, status

        user_type = token.get('type')
        if user_type != 'admin':
            response_object = {
                'status': 'failed',
                'message': 'User does not have admin rights.'
            }
            return response_object, 401

        return f(*args, **kwargs)

    return decorated

def root_token_required(f):
    wraps(f)
    def decorated(*args, **kwargs):

        data, status = Auth.get_logged_in_user(request)
        token = data.get('data')

        if not token:
            return data, status

        user_type = token.get('type')

        if user_type != 'root_admin':
            response_object = {
                'status': 'failed',
                'message': 'User is not root.'
            }
            return response_object, 401

        return f(*args, **kwargs)

    return decorated 