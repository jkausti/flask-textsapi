import unittest

from app.textsapi.service import s3buckets
from app.tests.base import BaseTestCase
from app.textsapi.models.bucket import Bucket


class TestS3Buckets(BaseTestCase):
    def test_create_bucket(self):
        """
        Test the method for creating an S3 bucket in S3 and in Dynamodb.
        """
        username = self.new_user.username
        bucket = s3buckets.create_bucket(username)

        self.assertTrue(isinstance(bucket, Bucket))

    def test_add_file_and_get_object(self):
        """
        Test the method for adding texts to S3.
        """
        username = self.new_user.username
        bucket = s3buckets.create_bucket(username)
        bucket_name = bucket.bucket_name
        id = 0
        input = "This is a string."

        # add_file
        file_name = s3buckets.add_file(
            username=username, input=input, bucket_name=bucket_name, id=id
        )
        self.assertTrue(file_name == "unprocessed_{id}_{username}".format(id=id, username=username))

        # get_object
        object = s3buckets.get_object(bucket_name, file_name)
        self.assertTrue(object == input)

    def test_get_active_bucket_or_create_new(self):
        """
        Test for the method that returns a bucket.
        """

        # No bucket existing
        username = self.new_user.username
        bucket = s3buckets.get_active_bucket_or_create_new(username)
        self.assertTrue(isinstance(bucket, Bucket))

        # Bucket exists
        new_bucket = s3buckets.get_active_bucket_or_create_new(username)
        self.assertTrue(bucket.bucket_name == new_bucket.bucket_name)
