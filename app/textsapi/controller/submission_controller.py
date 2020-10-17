from flask import request
from flask_restplus import Resource, marshal, marshal

from ..util.dto import SubmissionDto, GetSubmissionsDto, GetSubmissionTextsDto
from ..service.submission_service import (
    save_new_submission,
    get_user_submissions,
    get_submission_texts
)
from ..service.auth_helper import Auth
from ..util.decorator import admin_token_required, token_required

api = SubmissionDto.api
_submission_payload = SubmissionDto.submission_payload
_submission_response = SubmissionDto.submission_response
_get_submission = GetSubmissionsDto.get_submissions
_status = GetSubmissionsDto.status
_get_submission_texts = GetSubmissionTextsDto.get_submission_texts


@api.route('/')
class Submission(Resource):
    @api.response(201, 'Texts successfully submitted.')
    @api.doc(description='Use this method to submit texts per the example on the right.', body=_submission_payload)
    @api.expect(_submission_payload, validate=True)
    @token_required
    def post(self):
        """Submits texts"""
        data = request.json
        user_data, status = Auth.get_logged_in_user(request)
        if status == 200:
            username = user_data['data']['username']
            response, code = save_new_submission(data, username)
            return marshal(response, _submission_response, skip_none=True), code
        else:
            return marshal(user_data, _submission_response, skip_none=True), status

    @api.response(200, 'Request successful.')
    @api.doc(description='Get a list of all your submissions.')
    @api.marshal_list_with(_get_submission, envelope='data', skip_none=True)
    @token_required
    def get(self):
        """Gets a list of submissions for one user"""
        user_data, status = Auth.get_logged_in_user(request)
        if status == 200:
            username = user_data['data']['username'] 
            return get_user_submissions(username)
        else:
            return user_data, status


@api.route('/<int:submission_id>')
@api.param('submission_id', 'submission public identifier')
@api.response(400, 'submission id not found')
class SubmissionUpdate(Resource):
    # @api.response(200, 'Request successful')
    # @api.doc('Get a list of texts in submission')
    # @api.marshal_list_with(_submission, skip_none=True)
    # @token_required
    # def put(self, submission_id):
    #     """Updates a submission made by a user"""
    #     data = request.json
    #     user_data, status = Auth.get_logged_in_user(request)
    #     if status == 200:
    #         username = user_data['data']['username']
    #         return update_submission(data, username, submission_id)
    #     else:
    #         return user_data, status

    @api.response(200, 'request successful')
    @api.doc(description='Get a list of all texts in the submission. This endpoint will also return the processed data.')
    @api.marshal_list_with(_get_submission_texts, skip_none=True)
    @token_required
    def get(self, submission_id):
        """Returns the texts submitted in the submission with the processed data"""
        user_data, status = Auth.get_logged_in_user(request)
        if status == 200:
            username = user_data['data']['username']
            return get_submission_texts(username, submission_id)
        else:
            return user_data, status
