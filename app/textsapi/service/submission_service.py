import datetime
import traceback
import json

from pynamodb.models import DoesNotExist
from contextlib import suppress
from ..models.submission import Submission
from ..models.text import Text
from ..models.bucket import Bucket
from .auth_helper import Auth
from .s3buckets import (
    get_active_bucket_or_create_new,
    add_file,
    delete_objects,
    add_preprocessed_file,
    get_object
)
from pynamodb.connection import Connection


def save_new_submission(data, username):
    try:
        sort, pub_id = _create_sort_key(username)
        new_submission = Submission(
            username=username,
            sort=sort,
            text_count=len(data['submitted_texts']),
            submitted_date=datetime.datetime.utcnow(),
            public_id=pub_id
        )
        try:
            data['tags']
            new_submission.tags = data['tags']
        except Exception:
            print('No tags')
        data, status = save_texts(
            data['submitted_texts'], username, new_submission.public_id)
        if status == 201:
            new_submission.save()
            response_object = {
                'status': 'success',
                'message': 'successfully stored texts in database'
            }
            return response_object, 201
        else:
            return data, status
    except Exception:
        traceback.print_exc()
        response_object = {
            'status': 'failed',
            'message': "Something went wrong. Try again."
        }
        return response_object, 500


def get_all_submissions(username):
    range_cond = Submission.sort.startswith("SUBMISSION_")
    return [sub for sub in Submission.query(hash_key=username, range_key_condition=range_cond)]


def get_user_submissions(username):
    sub_condition = Submission.sort.startswith('SUBMISSION_')
    submissions = [sub for sub in Submission.query(
        hash_key=username, range_key_condition=sub_condition)]
    texts = [t for t in Text.query(
        hash_key=username, range_key_condition=Text.sort.startswith('TEXT_'))]

    response_object = []

    for sub in submissions:
        response_object.append(
            {
                'submission_id': sub.public_id,
                'text_count': sub.text_count,
                'submitted_date': sub.submitted_date,
                'tags': sub.tags if sub.tags else None,
                'texts': [text for text in texts if text.submission_id == sub.public_id]
            }
        )

    return response_object, 200


# def update_submission(data, username, submission_id):
#     try:
#         # fetch texts with same submission id as in given parameter
#         try:
#             sub = Submission.get(
#                 hash_key=username,
#                 range_key='SUBMISSION_{id}'.format(id=submission_id)
#             )
#         except Exception as e:
#             traceback.print_exc()
#             response_object = {
#                 'status': 'failed',
#                 'message': 'ID not in database. {}'.format(e)
#             }
#             return response_object, 404
#         text_range_condition = Text.sort.startswith('TEXT_')
#         text_filter_condition = Text.submission_id == submission_id
#         texts = Text.query(
#             hash_key=username,
#             range_key_condition=text_range_condition,
#             filter_condition=text_filter_condition
#         )

#         # create a dictionary of bucket ids and corresponding texts to be deleted
#         # NOTE: Initially, texts in same submission will get stored in same bucket
#         # bucket_id_dict = {k: [] for k in set([t.bucket_id for t in texts])}

#         bucket_items = {}
#         items = []
#         for t in texts:
#             items.append((t.bucket_id, t.raw_text_path))
#             t.delete()
        
#         for k, v in items:
#             bucket_items.setdefault(k, []).append(v)

#         # delete texts in S3 and handle exceptions
#         for k in bucket_items.keys():
#             deleted_objects = delete_objects(username, k, bucket_items[k])
#             if len(deleted_objects) == 0:
#                 response_object = {
#                     'status': 'failed',
#                     'message': 'Could not update submission.'
#                 }
#                 return response_object, 500
#             elif not len(set(deleted_objects).difference(set(bucket_items[k]))) == 0:
#                 response_object = {
#                     'status': 'failed',
#                     'message': 'Could not update submission. Please contact support.'
#                 }
#             else:
#                 pass  # all ok

#         new_submission = Submission(
#             username=username,
#             sort='SUBMISSION_{}'.format(str(submission_id)),
#             text_count=len(data['submitted_texts']),
#             submitted_date=datetime.datetime.utcnow(),
#             public_id=submission_id
#         )
#         try:
#             tags = data['tags']
#             new_submission.tags = tags
#         except Exception:
#             pass

#         data, status = save_texts(
#             data['submitted_texts'],
#             username, submission_id
#         )
#         if status == 201:
#             new_submission.save()
#             response_object = {
#                 'status': 'success',
#                 'message': 'submission with id {} updated'.format(submission_id)
#             }
#             return response_object, 201
#         else:
#             return data, status
#     except Exception:
#         traceback.print_exc()
#         response_object = {
#             'status': 'failed',
#             'message': "Something went wrong. Try again."
#         }
#         return response_object, 500


def save_texts(submitted_texts, username, submission_id):
    """
    Saves the submitted texts to an S3 bucket and creates the necessary
    metadata in the DB.
    """

    # Create texts in S3
    max_id = _get_max_sort_id(username)
    new_ids = [max_id+i for i in range(0, max_id+len(submitted_texts))]
    bucket = get_active_bucket_or_create_new(username)

    if not isinstance(bucket, Bucket):
        return bucket
    try:
        texts = [
            Text(
                username=username,
                sort='TEXT_{}'.format(i),
                bucket_id=bucket.public_id,
                raw_text_path=add_file(username, t, bucket.bucket_name, i),
                preprocessed_text_path=add_preprocessed_file(username, t, bucket.bucket_name, i),
                submission_id=submission_id,
                public_id=i
            ) for i, t in zip(new_ids, submitted_texts)
        ]
        for text in texts:
            text.save()
        response_object = {
            'status': 'success',
            'message': 'texts created'
        }
        return response_object, 201
    except Exception:
        traceback.print_exc()
        response_object = {
            'status': 'failed',
            'message': 'Could not create texts. Please try again or contact support.'
        }
        return response_object, 401


def get_submission_texts(username, submission_id):
    """
    This function fetches all the texts in a submission.
    It gives both the raw text and the processed text.

    The function returns a json response.
    """
    try:
        sub = Submission.get(
        hash_key=username,
        range_key='SUBMISSION_{}'.format(submission_id)
    )
    except DoesNotExist:
        traceback.print_exc()
        response_object = {
            'status': 'failed',
            'message': 'Submission ID not in database.'
        }
        return response_object, 400
    except Exception:
        traceback.print_exc()
        response_object = {
            'status': 'failed',
            'message': 'Unknown exception occured'
        }
        return response_object, 500

    try:
        filter_cond = Text.submission_id == submission_id
        range_cond = Text.sort.startswith('TEXT_')
        texts = [text for text in Text.query(
            hash_key=username,
            range_key_condition=range_cond,
            filter_condition=filter_cond
        )]

        # fetch texts from S3
        text_response = []
        for text in texts:
            

            text_item = {
                'text_id': text.public_id,
                'processing_complete': text.processing_complete,
                'raw_text': get_object(
                    bucket_name=Bucket.get(hash_key=text.username, range_key="BUCKET_{}".format(text.bucket_id)).bucket_name,
                    key=text.raw_text_path
                ),
                'processed_text': json.loads(
                    get_object(
                        bucket_name=Bucket.get(hash_key=text.username, range_key="BUCKET_{}".format(text.bucket_id)).bucket_name,
                        key=text.processed_text_path
                )) if text.processing_complete else None
            }
            text_response.append(text_item)

        response_object = {}
        response_object['submission'] = {
            'submission_id': sub.public_id,
            'text_count': sub.text_count,
            'submitted_date': sub.submitted_date,
            'tags': sub.tags if sub.tags else None
            }
        response_object['texts'] = text_response

        return response_object, 200
    except Exception:
        traceback.print_exc()
        response_object = {
            'status': 'failed',
            'message': 'server error'
            }
        return response_object, 500

"""
HELPER FUNCTIONS
"""


def _create_sort_key(username):
    new_id = 1
    condition = Submission.sort.startswith('SUBMISSION')
    for s in Submission.query(hash_key=username, range_key_condition=condition):
        if int(s.sort.split('_')[1]) >= new_id:
            new_id = int(s.sort.split('_')[1]) + 1

    return ('SUBMISSION_{}'.format(str(new_id)), new_id)


def _get_max_sort_id(username):
    new_id = 1
    condition = Text.sort.startswith('TEXT')
    for t in Text.query(hash_key=username, range_key_condition=condition):
        if int(t.sort.split("_")[1]) >= new_id:
            new_id = int(t.sort.split("_")[1]) + 1

    print("new_id: {}".format(new_id))
    return new_id
