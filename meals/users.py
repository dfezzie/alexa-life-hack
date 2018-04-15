from .models import User
from flask_ask import context
from .database import db_session

def get_current_user_id():
    return context['System']['user']['userId']

def get_user():
    """
    Return the current request user
    """
    amazon_id = get_current_user_id()
    return User.query.filter(User.amazon_id == amazon_id).first()

def check_user():
    """
    Check if the user exists in the database
    """
    amazon_id = get_current_user_id()
    user = User.query.filter(User.amazon_id == amazon_id).first()
    return True if user else False

def create_user():
    """ Create a user in the database.
    Uses the `get_current_user_id` method to parse id from context
    and creates the user in the database.

    Returns:
        User object
    """
    amazon_id = get_current_user_id()
    user = User(amazon_id=amazon_id)
    db_session.add(user)
    db_session.commit()