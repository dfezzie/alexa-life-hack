from datetime import date, timedelta

from meals import models
from meals.database import init_db, db_session
from meals.models import User, Dinner


amazon_id = 'amzn1.ask.account.AGUKR4U5SS7HVCP7GTBBVN7MSDV4F27ZZXJLYK3C2TDGMNTUOATN3OPBFJDOLXL3O6NBO7F4AUK5AB6NNNLACDZBBNALYZVQQEYFK4MINEWFSI6UUT4OV3XSNQC4IRBLN3P6A626A6AJSM6ODSUVG6XR64Q3OVYX3ZBYFV44DURCED6PG6E7P3X2PV7P3VIBCZODC5PP44XIIOY'
init_db()

user1 = User(
    amazon_id=amazon_id)
db_session.add(user1)
db_session.commit()

user1 = User.query.filter(User.amazon_id == amazon_id).first()

meal1 = Dinner(name='chicken', rating=7, date=(date.today() - timedelta(days=3)), user_id=user1.id)
meal2 = Dinner(name='pork', rating=8, date=(date.today() - timedelta(days=2)), user_id=user1.id)
meal3 = Dinner(name='pork', rating=5, date=(date.today() - timedelta(days=1)), user_id=user1.id)
meal4 = Dinner(name='riggatoni', rating=10, date=date.today(), user_id=user1.id)



db_session.add(meal1)
db_session.add(meal2)
db_session.add(meal3)
db_session.add(meal4)
db_session.commit()
