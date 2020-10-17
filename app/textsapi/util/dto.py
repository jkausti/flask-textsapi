from flask_restplus import Namespace, fields


class UserDto:
    api = Namespace('user', description="user-related operations")

    status = api.model('status', {
        'status': fields.String(description="Request status"),
        'message': fields.String(description="Message describing the status")
    })

    user = api.inherit('user', status, {
        'username': fields.String(required=True, description="unique alias"),
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description="user password"),
        'public_id': fields.Integer(description="user identifier")
    })


class SubmissionDto:
    api = Namespace(
        'submission', description="Submission-related operations.")

    status = api.model('Status', {
        'status': fields.String(description="Request status"),
        'message': fields.String(description="Message describing the status")
    })

    submission_payload = api.model('Submission payload', {
        'submitted_texts': fields.List(required=True, cls_or_instance=fields.String()),
        'tags': fields.List(cls_or_instance=fields.String(), description='tags related to submission')
    })

    submission_response = api.inherit('Submission response', status, {
        'submitted_texts': fields.List(required=True, cls_or_instance=fields.String()),
        'tags': fields.List(cls_or_instance=fields.String(), description='tags related to submission')
    })


class GetSubmissionsDto:
    api = Namespace('get submissions',
                    description='submission-related get-operations')

    status = api.model('Status', {
        'status': fields.String(description="Request status"),
        'message': fields.String(description="Message describing the status")
    })

    text_fields = {
        'text_id': fields.Integer(attribute='public_id', description='Public ID of text'),
        'processing_complete': fields.Boolean(description='Boolean indicating if text has been processed or not.'),
        'processing_started': fields.DateTime(description='date and timen when processing of text has started'),
        'processing_finished': fields.DateTime(description='date and time when processing of text has finished')
    }

    get_submissions = api.inherit('get submissions', status, {
        'submission_id': fields.Integer(required=True, description='submission identifier.'),
        'text_count': fields.Integer(required=True, description='Number of texts in submission.'),
        'submitted_date': fields.DateTime(required=True, description='date of submission'),
        'tags': fields.List(cls_or_instance=fields.String(), description='submission tags'),
        'texts': fields.List(cls_or_instance=fields.Nested(text_fields), description='list of text fields')
    })

class GetSubmissionTextsDto:
    api = Namespace('get submission texts', description='submission-specific get operations')

    status = api.model('Status', {
        'status': fields.String(description="Request status"),
        'message': fields.String(description="Message describing the status")
    })

    tags = {
        '*': fields.Wildcard(fields.String)
    }

    token = {
        "word": fields.String(description='original word'),
        "lemma": fields.String(description='lemma of original word'),
        "tags": fields.Nested(tags)
    }

    tokens = {
        "tokens": fields.List(cls_or_instance=fields.Nested(token), description='list of tokens')
    }

    sentences = {
        "sentences": fields.List(cls_or_instance=fields.Nested(tokens), description='list of sentences')
    }
    text_fields = {
        'text_id': fields.Integer(description='text identifier'),
        'processing_complete': fields.Boolean(description='Boolean indicating if text has been processed'),
        'raw_text': fields.String(description='Original text input'),
        'processed_text': fields.Nested(sentences)
    }

    submission_fields = {
        'submission_id': fields.Integer(description='submission identifier'),
        'text_count': fields.Integer(description='number indicating the amount of texts in submission'),
        'submitted_date': fields.DateTime(description='date of submission'),
        'tags': fields.List(cls_or_instance=fields.String(), description='submission tags')
    }

    get_submission_texts = api.inherit('get submission texts', status, {
        'submission': fields.Nested(submission_fields, default=dict()),
        'texts': fields.List(cls_or_instance=fields.Nested(text_fields))
    })

class TextDto:
    api = Namespace('text', description='Text-related operations')

    status = api.model('status', {
        'status': fields.String(description="request status"),
        'message': fields.String(description="status message")
    })

    tags = {
        '*': fields.Wildcard(fields.String)
    }

    token = {
        "word": fields.String(description='original word'),
        "lemma": fields.String(description='lemma of original word'),
        "tags": fields.Nested(tags)
    }

    tokens = {
        "tokens": fields.List(cls_or_instance=fields.Nested(token), description='list of tokens')
    }

    sentences = {
        "sentences": fields.List(cls_or_instance=fields.Nested(tokens), description='list of sentences')
    }

    text = api.inherit('text_details', status, {
        'id': fields.Integer(description='public id of text'),
        'submitted_date': fields.DateTime(description='Time text was submitted'),
        'processing_complete': fields.Boolean(description='indicates if text is processed or not'),
        'raw_text': fields.String(description="raw submitted text"),
        'processed_text': fields.Nested(sentences, default=dict())
    })


class AuthDto:
    api = Namespace('auth', description='Authentication-related operations')

    response = api.model('status', {
        'status': fields.String(description="request status"),
        'message': fields.String(description="message describing the status"),
        'authorization': fields.String(description="authorization token")
    })

    user_auth_request = api.model('login', {
        'username': fields.String(required=True, description='User alias.'),
        'password': fields.String(required=True, description='User password.')
    })
