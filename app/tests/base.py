from flask_testing import TestCase
from manage import app

from ..textsapi.models.user import User

import datetime
import os
import boto3


class BaseTestCase(TestCase):
    """ Base Tests """

    token = None
    new_user = None

    def create_app(self):
        app.config.from_object("app.textsapi.config.TestConfig")
        return app

    def setUp(self):
        self.new_user = User(
            username="tester_bot",
            sort="customer",
            email="email@email.com",
            registered_on=datetime.datetime.utcnow(),
            public_id=123,
        )
        self.new_user.password = "password_bot"
        self.new_user.save()

        self.token = self.new_user.encode_auth_token(
            self.new_user.username, self.new_user.sort
        ).decode()

    def tearDown(self):
        # Delete DB records
        for item in User.scan(attributes_to_get=[User.username, User.sort]):
            if item.username == "tester_bot" and item.sort == "customer":
                continue
            else:
                item.delete()

        # Delete S3 buckets and contents
        client = boto3.client("s3")
        response = client.list_buckets()

        for bucket in response["Buckets"]:
            if "-test-" in bucket["Name"]:
                # Delete content
                bucket = boto3.resource("s3").Bucket(bucket["Name"])
                bucket.objects.all().delete()

                # Delete bucket
                bucket.delete()
