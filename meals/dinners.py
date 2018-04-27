import logging

from .database import db_session
from .models import Dinner
from .users import get_user, check_user, create_user

log = logging.getLogger('flask_ask')
log.setLevel(logging.DEBUG)


def get_dinner_date(date):
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

def get_all_dinners(dinner):
    """Gets all instances of dinner with specified name.

    Args:
        dinner (str): Name of the dinner
    
    Returns:
        Collection of dinners, or none
    """
    user = get_user()
    dinners = Dinner.query.filter(Dinner.user_id == user.id).filter(Dinner.name == dinner).all()
    return dinners


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

