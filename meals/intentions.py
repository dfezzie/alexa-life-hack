import logging

from datetime import date as dt

from flask import Blueprint, render_template
from flask_ask import Ask, question, statement, session, delegate, confirm_intent, context, request

from .database import db_session
from .models import Dinner
from .users import get_user, check_user, create_user


blueprint = Blueprint('blueprint_api', __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

log = logging.getLogger('flask_ask')
log.setLevel(logging.DEBUG)
small_image_url = 'https://images.vexels.com/media/users/3/136264/isolated/preview/485f67bacd0d565a6d8732d3441059d9-kitchen-choppers-round-icon-by-vexels.png'
large_image_url = 'https://images.vexels.com/media/users/3/136264/isolated/preview/485f67bacd0d565a6d8732d3441059d9-kitchen-choppers-round-icon-by-vexels.png'

def get_dinner_query(date):
    """ Gets the dinner for a specified date.

    Args:
        date (date): Object
    Returns:
        Dinner object
    """
    log.debug('Getting Dinner with Date: ' + str(date))
    user = get_user()
    dinner = Dinner.query.filter(Dinner.date == date).filter(Dinner.user_id == user.id).first()
    return dinner

def get_confirmation_status():
    """
    Helper Function to get the confirmation status for a slot confirmation
    """
    log.debug('Getting Confirmation Status')
    return request['intent']['confirmationStatus']

def get_dialog_state():
    """
    Helper function to get the state of dialog.
    TODO: 
    Add Possible States here
    """
    return session['dialogState']


def check_dinner(date):
    """ Check if the date has a dinner set.

    Args:
        date (date): Date to check for dinner

    Returns:
        bool - True if day has dinner set
    """
    log.debug('Checking dinner with date:' + str(date))
    user = get_user()
    dinner = Dinner.query.filter(Dinner.date == date).filter(Dinner.user_id == user.id).first()
    print(dinner)
    return True if dinner else False

def set_dinner(name, date):
    """ Sets the dinner for a certain date

    Overrides any existing dinner for that day.

    Args:
        dinner(string): Name of the dinner.
        date (date): Date to set the dinner for.
    """
    # Get the current day dinner
    log.debug('Setting {} as dinner for day {}'.format(name, date))
    user = get_user()
    dinner = Dinner.query.filter(Dinner.date == date).filter(Dinner.user_id == user.id).first()
    if dinner:
        log.debug('Overriding dinner: ' + dinner.name)
        dinner.name = name
    else:
        log.debug('Creating new dinner')
        dinner = Dinner(name=name, date=date, user_id=user.id)
    db_session.add(dinner)
    db_session.commit()


def set_rating(rating):
    log.debug('Setting rating for today.')
    dinner = get_dinner_query(dt.today())
    if not dinner:
        return False
    dinner.rating = rating
    db_session.add(dinner)
    db_session.commit()
    return True

@ask.launch
def launch():
    """ Handles a hard launch of the app. First time users have an account created."""
    if check_user():
        speech_text = """Welcome back to Kitchenly Dinner Manager! What would you like to do?"""
    else:
        speech_text = """Welcome to Kitchenly Dinner Manager! Use Kitchenly to set dinners, and keep track 
        of your favorites. Ask for help for more information. What would you like to do today?"""
        create_user()

    return question(speech_text)


@ask.intent('SetDinnerSingle')
def set_dinner_single(dinner=None):
    confirm_status = get_confirmation_status()
    if confirm_status == 'DENIED':
        return statement('Okay.')
    log.debug('Set Dinner Single Confirmation Status is: ' + confirm_status)
    if dinner:
        log.debug('Set Dinner Single Dinner Specified')
        if check_dinner(date=dt.today()) and confirm_status != 'CONFIRMED':
            log.debug('Set Dinner Single Dinner Exists for Today')
            # Dinner set for today
            speech_text = """You already have {} set for tonight.
            Would you like to change it to {}?""".format(
                get_dinner_query(dt.today()).name,
                dinner)
            return confirm_intent(speech_text)
        else:
            log.debug('Set Dinner Single Setting Dinner to: ' + dinner)
            set_dinner(name=dinner, date=dt.today())
            return statement('Dinner has been set! Don\'t forget to rate the dinner after!')
    else:
        log.debug('Set Dinner Single Delegate')
        return delegate()


@ask.intent('GetDinner', convert={'request_date': 'date'})
def get_dinner(request_date):
    """ Get Dinner Intent is how a user gets the set dinner for a specific night
    
    The intent will use a default value of date, as sometimes the intent will be fore
    the current day, and the user will not specify a date.

    Args:
        date (date): Date the user specifies in the intent. Default today.
    """
    if not request_date:
        # Must be today
        request_date = dt.today()
    dinner = get_dinner_query(request_date)
    if not dinner:
        return statement('You do not have a dinner set.')
    dinner = dinner.name
    if request_date == dt.today():
        # Today
        speech_text = """You have {} set for tonight's dinner. Enjoy!""".format(dinner)
    elif request_date > dt.today():
        # Future tense
        speech_text = """You have {} planned for dinner on {}. Enjoy!""".format(dinner, request_date)
    else:
        # Past tense
        speech_text = """You had {}. I hope you enjoyed it!""".format(dinner)
    return statement(speech_text).standard_card(title='Kitchenly Helper',
                       text='{}'.format(speech_text),
                       small_image_url=small_image_url,
                       large_image_url=large_image_url)

@ask.intent('RateDinner', convert={'rating': int})
def rate_dinner(rating=None):
    if not rating:
        return delegate()
    if rating not in range(0, 11):
        # [0, 10]
        return statement('Rating must be between 0 and 10')
    success = set_rating(rating)
    if not success:
        # Dinner not set
        return statement('There is no dinner set for tonight.')
    if rating in range(5,8):
        # [5, 8)
        return statement('Dinner has been rated! See you tomorrow!')
    if rating < 5:
        return statement('Dinner has been rated! Hopefully dinner will be better tomorrow!')
    if rating > 7:
        return statement('Dinner has been rated! I\'m glad you enjoyed it!')
    return statement('Thanks for rating dinner!')

@ask.intent('GetRating', mapping={'amzn_dinner': 'dinner'})
def get_rating(amzn_dinner=None, request_date=None):
    speech_text = ''
    if not request_date and not amzn_dinner:
        # No args set.
        dinner = get_dinner_query(dt.today())
        if not dinner:
            return statement('You had no dinner set.')
        if dinner.rating is None:
            return statement('You have no rating for {}'.format(dinner.name))
        speech_text = 'You rated {} a {} out of 10'.format(dinner.name, dinner.rating)
    if request_date:
        # Request Dinner with a date
        dinner = get_dinner_query(request_date)
        if not dinner:
            return statement('You had no dinner set.')
        if dinner.rating is None:
            return statement('You have no rating for {}'.format(amzn_dinner))
        speech_text = 'You rated {} a {} out of 10'.format(amzn_dinner, dinner.rating)
    if amzn_dinner:
        # Get all instances of the dinner
        user = get_user()
        dinners = Dinner.query.filter(Dinner.user_id == user.id).filter(Dinner.name == amzn_dinner).all()
        if not dinners:
            return statement('You have never had {}'.format(amzn_dinner))
        num_times = len(dinners)
        rating_sum = 0
        rated_times = 0
        for meal in dinners:
            if meal.rating:
                rated_times += 1
                rating_sum += meal.rating
        average_rating = '%.1f' % (rating_sum / rated_times)
        if rated_times == 0:
            speech_text = 'You have had {} {} times, but have not rated it before'.format(
                dinner, num_times)
        speech_text = 'You have had {} {} times with an average of {} stars'.format(
            dinner, num_times, average_rating)
        
    return statement(speech_text)

@ask.intent('GetTopMeals', convert={'limit': int})
def get_top_meals(limit):
    if not limit:
        limit = 5
    if limit <= 0:
        return statement('You can only ask for a positive amount of top meals.')
    if limit > 10:
        limit = 10
    user = get_user()
    dinners = Dinner.query.filter(Dinner.user_id==user.id).order_by(Dinner.rating.desc()).limit(limit)
    speech_text = 'Your top {} dinners are: '.format(limit)
    i = 1
    for dinner in dinners:
        speech_text += 'Number {}: {} at {} stars.\n'.format(i, dinner.name, dinner.rating)
        i += 1
    return statement(speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = """Kitchenly Dinner Manager is a skill that allows you to track your dinner plans.
    You can set dinner by saying 'Today, I will be having the chicken soulvaki'.

    You can hear what you are having for dinner by asking, ', what am I having for dinner?'

    You can rate your dinner by saying, 'Kitchenly Dinner Manager, rate tonight's dinner as a 4.'
    """
    return statement(help_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement('Goodbye')


@ask.session_ended
def session_ended():
    return "{}", 200