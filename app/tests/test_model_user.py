import unittest
import datetime

from app.textsapi.models.user import User
from app.tests.base import BaseTestCase


class TestUserModel(BaseTestCase):
    def test_encode_auth_token(self):
        user = User(
            username="testuser",
            sort="customer",
            email="email@test.com",
            registered_on=datetime.datetime.utcnow(),
            public_id=100,
        )
        user.password = "testpass"
        user.save()
        auth_token = user.encode_auth_token(user.username, user.sort)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = User(
            username="testuser",
            sort="customer",
            email="email@test.com",
            registered_on=datetime.datetime.utcnow(),
            public_id=100,
        )
        user.password = "testpass"
        user.save()
        auth_token = user.encode_auth_token(user.username, user.sort)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token.decode("utf-8"))['sub'] == user.username)
