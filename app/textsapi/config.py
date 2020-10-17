import os


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'thisisasecretkey')
    DEBUG = False


class DevelopmentConfig(Config):
    DATABASE = 'textapi-dev'
    DEBUG = True
    RESTPLUS_MASK_SWAGGER = False
    SWAGGER_SUPPORTED_SUBMIT_METHODS = []


class TestConfig(Config):
    DATABASE = 'textapi-test'
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    RESTPLUS_MASK_SWAGGER = False


class ProductionConfig(Config):
    DATABASE = 'textapi-prod'
    DEBUG = False
    RESTPLUS_MASK_SWAGGER = False



config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestConfig,
    'prod': ProductionConfig
}

key = Config.SECRET_KEY