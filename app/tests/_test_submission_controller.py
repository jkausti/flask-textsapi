import unittest
import datetime
import json

from app.textsapi.models.submission import Submission
from app.textsapi.models.text import Text
from app.tests.base import BaseTestCase

def register_ok_submission(self, token):
    return self.client.post(
        '/submission/',
        headers=dict(
            Authorization="Token {}".format(token)
        ),
        data=json.dumps(dict(
            submitted_texts=['text1', 'text2']
        )),
        content_type='application/json'
    )

def register_illegal_submission(self, token):
    return self.client.post(
        '/submission/',
        headers=dict(
            Authorization="Token {}".format(token)
        ),
        data=json.dumps(dict(
            submitted_texts=[1, 'text2']
    )),
        content_type='application/json'
    )

def get_submissions(self, token):
    return self.client.get(
        '/submission/',
        headers=dict(
            Authorization="Token {}".format(token)
        )
    )


class TestSubmission(BaseTestCase):

    def test_create_valid_submission(self):
        """ Test for creating a valid submission """
        with self.client:
            # valid submission registration
            sub_response = register_ok_submission(self, self.token)
            response_data = json.loads(sub_response.data.decode())
            self.assertTrue(response_data['status']=='success')

    def test_create_invalid_submission(self):
        """ Test for creating an invalid submission """
        with self.client:
            # invalid submission registration
            sub_response = register_illegal_submission(self, self.token)
            response_data = json.loads(sub_response.data.decode())
            self.assertTrue(response_data['errors']!=None)

    def test_update_submission(self):
        """ Test for updating a submission """
        sub_response_register = register_ok_submission(self, self.token)
        response_data = json.loads(sub_response_register.data.decode())
        self.assertTrue(response_data['status']=='success')

        sub = [sub for sub in Submission.query(hash_key=self.new_user.username, range_key_condition=Submission.sort.startswith('SUBMISSION_'))][0]
        sub_response_update = self.client.put(
            '/submission/{}'.format(str(sub.public_id)),
            headers=dict(
            Authorization="Token {}".format(self.token)
            ),
            data=json.dumps(dict(
            submitted_texts=['updated_text1']
            )),
            content_type='application/json'
        )
        update_data = json.loads(sub_response_update.data.decode())
        upd_sub = Submission.get(hash_key=sub.username, range_key=sub.sort)
        self.assertTrue(update_data['status']=='success')
        self.assertTrue(upd_sub.text_count == 1)

    def test_get_submission(self):
        """ Test getting the submissions from database """
        # creating a submission
        sub_register = register_ok_submission(self, self.token)
        response_data = json.loads(sub_register.data.decode())
        self.assertTrue(response_data['status']=='success')

        # getting it from the service
        get_response = get_submissions(self, self.token)
        response_data = json.loads(get_response.data.decode())
        self.assertTrue(response_data['data'][0]['text_count']==2)
        self.assertTrue(isinstance(response_data['data'][0]['texts'], list))





if __name__ == '__main__':
    unittest.main()