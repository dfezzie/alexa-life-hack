import logging
from collections import defaultdict
import operator

from datetime import date as dt

from flask import Blueprint, render_template
from flask_ask import (Ask, question, statement, session, delegate, confirm_intent, context,
    request, convert_errors)

from .database import db_session
from .models import Dinner
from .users import get_user, check_user, create_user
from .dinners import get_dinner_date, check_dinner, set_dinner
from .ratings import set_rating, get_rating, average_rating

blueprint = Blueprint('blueprint_api', __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

log = logging.getLogger('flask_ask')
log.setLevel(logging.DEBUG)
small_image_url = 'https://images.vexels.com/media/users/3/136264/isolated/preview/485f67bacd0d565a6d8732d3441059d9-kitchen-choppers-round-icon-by-vexels.png'
large_image_url = 'https://images.vexels.com/media/users/3/136264/isolated/preview/485f67bacd0d565a6d8732d3441059d9-kitchen-choppers-round-icon-by-vexels.png'

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


@ask.launch
def launch():
    log.debug('Launch')
    """ Handles a hard launch of the app. First time users have an account created."""
    if check_user():
        log.debug('User Found!')
        speech_text = """Welcome back to Kitchenly Dinner Manager! What would you like to do?"""
    else:
        log.debug('User Not found. Creating.')
        speech_text = """Welcome to Kitchenly Dinner Manager! Use Kitchenly to set dinners, and keep track 
        of your favorites. Ask for help for more information. What would you like to do today?"""
        create_user()

    return question(speech_text).reprompt('I didn\'t get that. What would you like to do?')

@ask.intent('SetDinnerSingle')
def set_dinner_single(dinner=None):
    log.debug('Entering Set Dinner Single')
    if convert_errors:
        return question('I had trouble understanding you. Can you ask again?')
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
                get_dinner_date(dt.today()).name,
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
def get_dinner_intent(request_date):
    """ Get Dinner Intent is how a user gets the set dinner for a specific night
    
    The intent will use a default value of date, as sometimes the intent will be fore
    the current day, and the user will not specify a date.

    Args:
        date (date): Date the user specifies in the intent. Default today.
    """
    log.debug('GetDinner Intent')
    if convert_errors:
        return question('I had trouble understanding you. Can you ask again?')
    if not request_date:
        # Must be today
        request_date = dt.today()
    dinner = get_dinner_date(request_date)
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
def rate_dinner_intent(rating=None):
    log.debug('RateDinner Intent')
    if convert_errors:
        return question('I had trouble understanding you. Can you ask again?')
    if rating is None:
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
def get_rating_intent(amzn_dinner=None, request_date=None):
    log.debug('GetRating Intent')
    if convert_errors:
        return question('I had trouble understanding you. Can you ask again?')
    log.debug('Getting Rating for {} dinner or {} date'.format(amzn_dinner, request_date))
    speech_text = ''
    if not request_date and not amzn_dinner:
        # Get Dinner with today's date
        log.debug('No dinner or request date specified.')
        speech_text = get_rating(dt.today())
    if request_date:
        # Request Dinner with a date
        log.debug('Getting dinner with date: ' + request_date)
        speech_text = get_rating(request_date)
    if amzn_dinner:
        # Calculate average rating for specified dinner
        speech_text = average_rating(amzn_dinner)
    return statement(speech_text)

@ask.intent('GetTopMeals', convert={'limit': int})
def get_top_meals(limit):
    log.debug('GetTopMeals Intent')
    if convert_errors:
        return question('I had trouble understanding you. Can you ask again?')
    if not limit:
        limit = 5
    if limit <= 0:
        return statement('You can only ask for a positive amount of top meals.')
    if limit > 10:
        limit = 10
    user = get_user()
    dinners = Dinner.query.filter(Dinner.user_id==user.id).filter(Dinner.rating != None).all()

    dinner_count = defaultdict(int)
    total_ratings = defaultdict(int)
    for dinner in dinners:
        dinner_count[dinner.name] += 1
        total_ratings[dinner.name] += dinner.rating
    
    avg = {}
    for dinner in total_ratings.keys():
        avg[dinner] = total_ratings[dinner]/ dinner_count[dinner]
    
    # Sort dinner by average and limit it
    sorted_dinners = sorted(avg.items(), key=operator.itemgetter(1), reverse=True)[:limit]
    if limit > len(sorted_dinners):
        limit = len(sorted_dinners)
    speech_text = 'Your top {} dinners are: '.format(limit)
    i = 1
    for dinner in sorted_dinners:
        speech_text += 'Number %s: %s at %.1f stars.\n' % (i, dinner[0], dinner[1])
        i += 1
    print(dinners)

    if not dinners:
        speech_text = 'You have never rated a dinner before!'
    return statement(speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    log.debug('HelpIntent Intent')

    help_text = """Kitchenly Dinner Manager is a skill that allows you to track your dinner plans.
    
    You can set dinner by saying: 
    
    'Alexa, tell Dinner manager, I will be having chicken soulvaki'.

    You can hear what you are having for dinner by asking, dinner manager, what am I having for dinner?'

    You can rate your dinner by saying, 'Dinner Manager, rate tonight's dinner as a 4.'

    What would you like to do today?
    """
    return question(help_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    log.debug('Cancel Intent')
    return statement('Goodbye')


@ask.session_ended
def session_ended():
    log.debug('Session Ended Intent')
    return "", 200

@ask.intent('AMAZON.StopIntent')
def stop_intent():
    log.debug('Stop intent')
    return statement('Goodbye')
