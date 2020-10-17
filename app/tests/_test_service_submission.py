import unittest
import json

from app.tests.base import BaseTestCase
from app.textsapi.models.submission import Submission
from app.textsapi.service import submission_service


class TestServiceSubmission(BaseTestCase):
    def test_save_new_submission(self):
        """
        Tested method: save_new_submission

        Scenario 1: Legit input with 2 strings.
        Scenario 2: Non-legit input with an integer.
        """
        username = self.new_user.username
        print(username)
        data1 = {"submitted_texts": ["this is the first text", "this is the second text"]}
        data2 = {"submitted_texts": ["this is the first text", 5]}

        response1 = submission_service.save_new_submission(data1, username)
        response2 = submission_service.save_new_submission(data2, username)
        self.assertTrue(response1[0]["status"] == "success")
        self.assertTrue(response2[0]["status"] == "failed")
