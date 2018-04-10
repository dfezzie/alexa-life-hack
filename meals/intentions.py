import logging

from flask import Blueprint, render_template
from flask_ask import Ask, question, statement


blueprint = Blueprint('blueprint_api', __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launch():
    speech_text = "Welcome to kitchenly! Would you like to hear what's on the menu for tonight?"
    return question(speech_text)


@ask.intent('TodayDinnerIntent')
def today_dinner():
    speech_text = "Today you plan on having Chicken Soulvaki."
    return statement(speech_text)

@ask.intent('RateDinner')
def rate_dinner():
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


@ask.session_ended
def session_ended():
    return "{}", 200
