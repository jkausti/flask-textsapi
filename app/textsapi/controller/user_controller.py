from flask import request
from flask_restplus import Resource

from ..util.dto import UserDto
from ..util.decorator import admin_token_required, token_required, root_token_required
from ..service.user_service import save_new_user, get_a_user, get_all_users, create_admin_user

api = UserDto.api
_user = UserDto.user


@api.route('/', doc=False)
class UserList(Resource):
    @api.response(201, 'User successfully created.')
    @api.doc('create new user')
    @api.expect(_user, validate=True)
    @admin_token_required
    def post(self):
        """Creates new user."""
        data=request.json
        return save_new_user(data=data)

    @api.doc('get a list of users')
    @api.marshal_list_with(_user, envelope='data', skip_none=True)
    @admin_token_required
    def get(self):
        """Get a list of users"""
        return get_all_users()
        
@api.route('/<username>', doc=False)
@api.param('username', 'users unique alias')
@api.response(404, 'User not found')
class User(Resource):
    @api.doc('get a user')
    @api.marshal_with(_user, skip_none=True)
    @admin_token_required
    def get(self, username):
        user = get_a_user(username)
        if not user:
            api.abort(404)
        else:
            return user


@api.route('/admin', doc=False)
@api.response(201, 'Admin created.')
class AdminUser(Resource):
    @api.marshal_with(_user, skip_none=True)
    @root_token_required
    def post(self):
        data=request.json
        return create_admin_user(data)