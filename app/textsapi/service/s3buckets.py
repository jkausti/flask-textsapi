import boto3
import traceback
import datetime
import os

from botocore.exceptions import ClientError
from ..models.bucket import Bucket
from ..util.preprocessor import preprocess

"""
S3 functions
"""


def get_active_bucket_or_create_new(username):
    """
    Returns the user's current active bucket. If there are no buckets,
    or all the users buckets are full, a new one will be created first.

    returns: Bucket object
    """

    try:
        # queries database for non-full buckets
        range_cond = Bucket.sort.startswith("BUCKET_")
        buckets = Bucket.query(hash_key=username, range_key_condition=range_cond)

        # return existing if not full or create new
        for buck in buckets:
            if not buck.full:
                return buck
        else:
            bucket = create_bucket(username)
            return bucket
    except Exception as e:
        traceback.print_exc()
        response_object = {
            "status": "failed",
            "message": "Could not query buckets in DB. {}".format(e),
        }
        return response_object, 500


def create_bucket(username, region="eu-central-1"):
    """
    Creates an S3 bucket in S3.
    Naming format: 'flasktextapi-{ENV}-{USERNAME}-BUCKET{BUCKET_ID}'
    IMPORTANT: underscores in usernames are converted to dashes.

    returns: bucket
    """
    # create S3 bucket
    try:
        bucket_id = _generate_bucket_id(username)
        username_conv = username.replace("_", "-")
        bucket_name = "flasktextapi-{env}-{username}-bucket{id}".format(
            env=os.getenv("BOILERPLATE_ENV"), username=username_conv, id=bucket_id
        )
        bucket = boto3.resource("s3").Bucket(bucket_name)
        location = {"LocationConstraint": region}
        response = bucket.create(CreateBucketConfiguration=location)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            try:
                db_bucket = _create_db_bucket(username, bucket_id, bucket_name)
                return db_bucket
            except Exception:
                traceback.print_exc()
                response_object = {
                    "status": "failed",
                    "message": "Bucket created successfully but bucket details could not be stored to database.",
                }
                return response_object, 500
        else:
            response_object = {"status": "failed", "message": "could not create bucket"}
            return response_object, 500
    except Exception as e:
        traceback.print_exc()
        response_object = {
            "status": "failed",
            "message": "Could not create bucket. {}".format(e),
        }
        return response_object, 500


def add_file(username, input, bucket_name, id, region="eu-central-1"):
    """
    Adds a text to an S3 bucket.

    Naming format of file: 'unprocessed_{username}_{text.public_id}'

    @return: Name of the file as String.
    """

    # check input type
    if not isinstance(input, str):
        raise ValueError("Text needs to be a String.")

    bucket = boto3.resource("s3").Bucket(bucket_name)
    key = "unprocessed_{id}_{username}".format(id=id, username=username)
    bucket.put_object(Body=bytes(input, "utf-8"), Key=key)
    return key


def add_preprocessed_file(username, input, bucket_name, id, region="eu-central-1"):
    """
    Adds a text to an S3 bucket.

    Naming format of file: 'unprocessed_{username}_{text.public_id}'

    @return: Name of the file as String.
    """

    # check input type
    if not isinstance(input, str):
        raise ValueError("Text needs to be a String.")

    # preprocess input
    prepr_input = preprocess(input)

    bucket = boto3.resource("s3").Bucket(bucket_name)
    key = "preprocessed_{id}_{username}".format(id=id, username=username)
    bucket.put_object(Body=bytes(prepr_input, "utf-8"), Key=key)
    return key


def get_object(bucket_name, key):
    """
    Fetches an object from S3.

    returns: String
    """
    s3 = boto3.resource("s3")
    object = s3.Object(bucket_name, key)
    return object.get()["Body"].read().decode("utf-8")


def delete_objects(username, bucket_id, objects):
    """
    Deletes an object from an s3 bucket.

    Returns: List of deleted objects
    """
    db_bucket = Bucket.get(hash_key=username, range_key="BUCKET_{}".format(bucket_id))
    bucket = boto3.resource("s3").Bucket(db_bucket.bucket_name)

    delete_dict = {"Objects": [{"Key": name} for name in objects]}

    response = bucket.delete_objects(Delete=delete_dict)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        deleted_items = []
        for item in response["Deleted"]:
            deleted_items.append(item["Key"])
        return deleted_items
    else:
        deleted_items = []
        return deleted_items


"""
DB Functions related to S3
"""


def _create_db_bucket(username, id, bucket_name):
    new_bucket = Bucket(
        username=username,
        sort="BUCKET_{}".format(id),
        bucket_name=bucket_name,
        created_date=datetime.datetime.utcnow(),
        public_id=id,
        full=False,
    )
    new_bucket.save()
    return new_bucket


"""
Helper functions
"""


def _generate_bucket_id(username):
    full_buckets = Bucket.query(
        hash_key=username, range_key_condition=Bucket.sort.startswith("BUCKET_")
    )
    new_id = 0

    for buck in full_buckets:
        if buck.public_id > new_id:
            new_id = buck.public_id + 1

    return new_id


def _bucket_full(bucket_name):
    bucket = boto3.resource("s3").Bucket(bucket_name)
    size = sum([object.size for object in bucket.objects.all()])

    if size > 4990000000000:
        return True
    else:
        return False
