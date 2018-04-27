import logging
from datetime import date

from .dinners import get_dinner_date, get_all_dinners
from .database import db_session

log = logging.getLogger('flask_ask')
log.setLevel(logging.DEBUG)

def set_rating(rating):
    log.debug('Setting rating for today.')
    dinner = get_dinner_date(date.today())
    if not dinner:
        return False
    dinner.rating = rating
    db_session.add(dinner)
    db_session.commit()
    return True


def get_rating(request_date):
    """Gets the rating for the dinner that was set for that day.

    """
    dinner = get_dinner_date(request_date)
    if not dinner:
        return 'You had no dinner set.'
    if dinner.rating is None:
        return 'You have no rating for {}'.format(dinner.name)
    return 'You rated {} a {} out of 10'.format(dinner.name, dinner.rating)


def average_rating(dinner:str):
    """ Returns speech text for 
    """
    log.debug('Getting average rating for: ' + dinner)
    dinners = get_all_dinners(dinner)
    if not dinners:
        return 'You have never had ' + dinner

    # Calculate average ratings
    num_times = len(dinners)
    rating_sum = 0
    rated_times = 0
    for meal in dinners:
        if meal.rating:
            rated_times += 1
            rating_sum += meal.rating
    average_rating = '%.1f' % (rating_sum / rated_times)
    if rated_times == 0:
        # User has never rated the dinner
        return 'You have had {} {} times, but have not rated it before.'.format(
            dinner, num_times)
    return 'You have had {} {} times with an average of {} stars.'.format(
        dinner, num_times, average_rating)