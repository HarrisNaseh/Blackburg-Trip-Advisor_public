from TripAdvisor import db, login_manager
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(), nullable = False)
    last_name = db.Column(db.String(), nullable = False)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(70), nullable = False)

@login_manager.user_loader
def load_user(user):
    return User.query.get(int(user))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(), nullable=False, default = "")

    # Use back_populates instead of backref to avoid conflicts
    categories = db.relationship(
        'Category',
        secondary='event_category',
        back_populates='events',  # Specify the back_populates field
        lazy='dynamic',
    )


class EventCategories(db.Model):
    __tablename__ = 'event_category'
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Use back_populates instead of backref to avoid conflicts
    events = db.relationship(
        'Event',
        secondary='event_category',
        back_populates='categories',  # Match the back_populates field in Event
        lazy='dynamic',
    )


