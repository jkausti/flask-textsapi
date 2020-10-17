from flask import request
from flask_restplus import Resource, marshal

from ..service.auth_helper import Auth
from ..util.dto import AuthDto
from ..util.decorator import token_required

api = AuthDto.api
user_auth_request = AuthDto.user_auth_request
user_auth_response = AuthDto.response


@api.route('/obtain_token')
class ObtainToken(Resource):
    @api.doc(description="""This endpoint is used to obtain a token needed to use the service.
    Tokens are valid for 24 hours.""")
    @api.expect(user_auth_request, validate=True)
    def post(self):
        post_data = request.json
        response, code = Auth.obtain_user_token(data=post_data)
        return marshal(response, user_auth_response, skip_none=True), code

@api.route('/obtain_admin_token', doc=False)
class ObtainAdminToken(Resource):
    @api.expect(user_auth_request, validate=True)
    def post(self):
        data = request.json
        response, code = Auth.obtain_admin_token(data=data)
        return marshal(response, user_auth_response, skip_none=True), code

@api.route('/obtain_root_token', doc=False)
class ObtainRootToken(Resource):
    @api.expect(user_auth_request, validate=True)
    def post(self):
        data = request.json
        response, code = Auth.obtain_root_token(data=data)
        return marshal(response, user_auth_response, skip_none=True), code

@api.route('/destroy_token')
class DestroyToken(Resource):
    @api.doc(description="""This endpoint is used to destroy a token 
    so that it cannot be used anymore even though if it would still be valid.""")
    @token_required
    def post(self):
        auth_header = request.headers.get('Authorization')
        return Auth.destroy_user_token(data=auth_header)