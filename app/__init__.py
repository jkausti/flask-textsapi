# app/__init__.py

from flask_restplus import Api
from flask import Blueprint

from .textsapi.controller.user_controller import api as user_ns
from .textsapi.controller.auth_controller import api as auth_ns
from .textsapi.controller.submission_controller import api as sub_ns
from .textsapi.controller.text_controller import api as text_ns


blueprint = Blueprint('api', __name__)
#authorizations = {
#    'apikey': {
#        'type': 'apiKey',
#        'in': 'header',
#        'name': 'Authorization'
#    }
#}

api = Api(
    blueprint,
    title="LINGV.IO NLP API Documentation",
    version='0.1',
    description="An NLP API for Finnish data. <style>.models {display: none !important}</style>",
#    authorizations=authorizations
)

api.add_namespace(user_ns, path='/user')
api.add_namespace(auth_ns)
api.add_namespace(sub_ns, path='/submission')
api.add_namespace(text_ns, path='/text')
