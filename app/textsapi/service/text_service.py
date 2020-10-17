import traceback
import json

from pynamodb.models import DoesNotExist
from ..models.text import Text
from ..models.bucket import Bucket
from ..models.submission import Submission

from ..service.s3buckets import get_object


def get_text(username, text_id):
    """
    Method that fetches the requested text from DB and S3.
    """
    try:
        text = Text.get(hash_key=username, range_key="TEXT_{}".format(text_id))
    except DoesNotExist:
        response_object = {
            'status': 'failed',
            'message': 'Text ID not in database.'
        }
        return response_object, 400
    try:
        bucket = Bucket.get(hash_key=username, range_key="BUCKET_{}".format(text.bucket_id))
        submission = Submission.get(
            hash_key=username, range_key="SUBMISSION_{}".format(text.submission_id)
        )

        raw_text = get_object(bucket.bucket_name, text.raw_text_path)
        processed_text = json.loads(get_object(bucket.bucket_name, text.processed_text_path))

        response_object = {
            "id": text.public_id,
            "submitted_date": submission.submitted_date,
            "processing_complete": text.processing_complete,
            "raw_text": raw_text,
            "processed_text": processed_text,
        }
        return response_object, 200
    except Exception:
        traceback.print_exc()
        response_object = {
            'status': 'failed',
            'message': 'server error'
            }
        return response_object, 500
