import uuid
import datetime
import traceback

from ..models.user import User
from pynamodb.exceptions import DoesNotExist


def save_new_user(data):
    """
    Saves data about a new user.
    """
    try:
        # User exists already
        User.get(data["username"], range_key="customer")
        response_object = {
            "status": "failed",
            "message": "User exists already, please login or register with another username.",
        }
        return response_object, 409

    except DoesNotExist:
        # Creates a new user
        new_user = User(
            username=data["username"],
            sort="customer",
            email=data["email"],
            registered_on=datetime.datetime.utcnow(),
            public_id=_create_new_id(),
        )
        new_user.password = data["password"]
        new_user.save()
        response_object = {"status": "success", "message": "Successfully registered"}
        return generate_token(new_user)
    except Exception:
        response_object = {
            "status": "failed",
            "message": "Error occured. Please contact system owner.",
        }
        return response_object, 500


def get_all_users():
    condition = User.sort == "customer"
    return [user for user in User.scan(filter_condition=condition)]


def get_a_user(username):
    try:
        user = User.get(hash_key=username, range_key="customer")
        return user
    except DoesNotExist:
        return (
            {"status": "failed", "message": "No user with that username exists in the database."},
            409,
        )
    except Exception:
        return {"status": "failed", "message": "An error occurred. Contact system owner."}, 500


def create_root_user(username, email, password):
    try:
        root_admin_list = User.scan(filter_condition=(User.sort == "root_admin"))
        if root_admin_list.total_count > 0:
            return "Root user exists already."
        else:
            root_user = User(
                username=username,
                sort="root_admin",
                email=email,
                registered_on=datetime.datetime.utcnow(),
                public_id=_create_new_id(),
            )
            root_user.password = password
            root_user.save()
            return "Root user successfully created."
    except Exception:
        return "Root user could not be created."


def create_admin_user(data):
    try:
        User.get(data["username"], range_key="admin")
        response_object = {
            "status": "failed",
            "message": "User exists already, please login or register with another username.",
        }
        return response_object, 409

    except DoesNotExist:
        new_user = User(
            username=data["username"],
            sort="admin",
            email=data["email"],
            registered_on=datetime.datetime.utcnow(),
            public_id=_create_new_id(),
        )
        new_user.password = data["password"]
        new_user.save()
        response_object = {"status": "success", "message": "Successfully registered"}
        return generate_token(new_user)
    except Exception:
        response_object = {
            "status": "failed",
            "message": "Error occured. Please contact system owner.",
        }
        return response_object, 500


"""
HELPER FUNCTIONS
"""


def generate_token(user):
    try:
        # generate the auth token
        auth_token = user.encode_auth_token(user.username, user.sort)
        response_object = {
            "status": "success",
            "message": "Successfully registered",
            "Authorization": auth_token.decode(),
        }
        return response_object, 201
    except Exception:
        response_object = {
            "status": "failed",
            "message": "Unable to generate token. Please try again.",
        }
        return response_object, 401


def _create_new_id():
    new_id = 1000
    try:
        for user in User.scan(filter_condition=(User.sort == "customer")):
            if int(user.public_id) >= new_id:
                new_id = int(user.public_id) + 1
    except Exception:
        traceback.print_exc()

    return new_id
