from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, validates
from .database import Base

class User(Base):
    """
    Table that represents users in the system

    Args:
        id (primary key): Primary key of user
        amazon_id (str): ID of the user
        dinners (relationship): one to many relationship with dinners
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    amazon_id = Column(String, nullable=False)
    dinners = relationship('Dinner', backref='user', lazy=True)

    def __init__(self, amazon_id):
        self.amazon_id = amazon_id

    def __repr__(self):
        return '<User %r>' % (self.name)
    
class Dinner(Base):
    """
    Table that represents the dinner objects for a user
    
    Args:
        id (primary key): Primary key for dinner
        name (string): Name of the dinner
        user_id (relationship): Many to one relationship with User table
        date (date): Date the dinner was set for 
        rating (integer): Rating for the meals dinner. Constrained to (0, 5].
    """
    __tablename__ = 'dinners'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    rating = Column(Integer, nullable=True)

    def __init__(self, name, user_id, date, rating=None):
        self.name = name
        self.user_id = user_id
        self.date = date
        self.rating = rating

    def __repr__(self):
        return '<Dinner {} on {}>'.format(self.name, self.date)
    
    @validates('rating')
    def validate_rating(self, key, value):
        """
        Validator to ensure rating is (0, 5] or None
        """
        assert value is None or value <= 5 and value > 0
        return value
    