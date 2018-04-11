import logging

from datetime import date

from flask import Blueprint, render_template
from flask_ask import Ask, question, statement, context

from .database import db_session
from .models import User, Dinner

blueprint = Blueprint('blueprint_api', __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

log = logging.getLogger('flas_ask')
log.setLevel(logging.INFO)


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
    if user:
        return True
    else:
        return False

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

def check_dinner(date):
    """ Check if the date has a dinner set.

    Args:
        date (date): Date to check for dinner

    Returns:
        bool - True if day has dinner set
    """
    dinner = User.query.filter(Dinner.date == date).first()
    return True if dinner else False

def set_dinner(dinner, date):
    """ Sets the dinner for a certain date

    Overrides any existing dinner for that day.

    Args:
        dinner(string): Name of the dinner.
        date (date): Date to set the dinner for.
    """
    print(date)
    user = get_user()
    dinner = Dinner(name=dinner, date=date, user_id=user.id)
    db_session.add(dinner)
    db_session.commit()

@ask.launch
def launch():
    if check_user():
        speech_text = """Welcome back to kitchenly! 
        Would you like to hear what\'s on the menu for tonight?"""
    else:
        speech_text = """Welcome to kitchenly!
        Would you like to hear what's on the menu for tonight?"""
        create_user()

    return question(speech_text)


@ask.intent('TodayDinnerIntent')
def todays_dinner():
    speech_text = "Today you plan on having Chicken Soulvaki."
    return statement(speech_text)

@ask.intent('SetDinnerSingle')
def set_dinner_single(dinner=None):
    print(dinner)
    if dinner:
        if check_dinner(date=date.today()):
            # Dinner set for today
            speech_text = """You already have a dinner set for tonight.
            Would you like to change it to {}?""".format(dinner)
            return question(speech_text)
        else:
            # No dinner set
            set_dinner(dinner=dinner, date=date.today())
            return statement('Dinner has been set! Don\'t forget to rate the dinner after!')
    else:
        return question('What do you want for dinner tonight?')


@ask.intent('RateDinner')
def rate_dinner(dinner):
    speech_text = "How would you rate tonight's dinner?"
    return question(speech_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = """Kitchenly is a skill that allows you to track your dinner plans.
    You can set dinner by saying 'Today, I will be having the chicken soulvaki'.

    You can hear what you are having for dinner by asking, 'Kitchenly, what am I having for dinner?'

    You can rate your dinner by saying, 'Kitchenly, rate tonight's dinner as a 4.'
    """
    return statement(help_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement('Goodbye')


@ask.session_ended
def session_ended():
    return "{}", 200
