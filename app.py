import logging
import os

from flask import Flask
from meals.intentions import blueprint

app = Flask(__name__)
app.register_blueprint(blueprint)

logging.getLogger('flask_app').setLevel(logging.DEBUG)


if __name__ == '__main__':
    app.run(debug=True)