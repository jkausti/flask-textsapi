import os
import unittest
import argparse

from flask_script import Manager
from app.textsapi import create_app
from app import blueprint
from app.textsapi.service.user_service import create_root_user

app = create_app(os.getenv("BOILERPLATE_ENV") or "dev")
app.register_blueprint(blueprint)

app.app_context().push()

manager = Manager(app)


@manager.command
def run():
    app.run()


@manager.command
def root():
    """ Creates a root user """
    username = input("Please enter the root username: ")

    while len(username) < 4 or any(not c.isalnum() for c in username):
        username = input(
            "Root username needs to be at least 4 charachters long and only contain alphanumeric characters. Try again: "
        )

    email = input("Please enter the root email: ")
    password = input("Please enter the root password: ")

    spec = (" ", "_", "\n")
    while len(password) < 6 or any(c in spec for c in password):
        password = input(
            "Password cannot contain whitespaces or underscores and cannot be less than 6 characters long. Try again: "
        )

    return create_root_user(username, email, password)


# @manager.command
# def test():
#     """
#     Runs the unittests.
#     """
#     tests = unittest.TestLoader().discover("app/tests", pattern="test*.py")
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         return 0
#     return 1


@manager.command
def test(layer="*", component="*"):
    """
    Runs the unittests.
    """
    tests = unittest.TestLoader().discover(
        "app/tests", pattern="test_{layer}_{component}.py".format(layer=layer, component=component)
    )
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":
    manager.run()
