from flask import request
from flask_restplus import Resource

from ..util.decorator import token_required
from ..util.dto import TextDto
from ..service.text_service import get_text

from ..service.auth_helper import Auth

api = TextDto.api
_text = TextDto.text


@api.route('/<int:text_id>')
@api.param('text_id', 'text public identifier')
class Text(Resource):
    @api.response(200, 'Text successfully fetched')
    @api.doc(description='This method can be used to fetch data about a single text, instead of the whole submission.')
    @api.marshal_with(_text, skip_none=True, envelope='data')
    @token_required
    def get(self, text_id):
        user_data, status = Auth.get_logged_in_user(request)
        if status == 200:
            username = user_data['data']['username']
            return get_text(username, text_id)
        else:
            return user_data, status
