from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField, SelectMultipleField, \
    DecimalField, SelectField, DateTimeLocalField, PasswordField, TextAreaField, ValidationError, widgets
from wtforms.validators import DataRequired, Email, NumberRange, Length, EqualTo, Optional

from TripAdvisor.models import Category

class LoginForm(FlaskForm):
    username = StringField('UserName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label = False)
    option_widget = widgets.CheckboxInput()

class AddEventForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    start = DateTimeLocalField('Start Date and Time', validators=[DataRequired()])
    end = DateTimeLocalField('End Date and Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    categories = MultiCheckboxField('Categories', validators=[Optional()])

    submit = SubmitField('Add Event')

    def __init__(self, *args, **kwargs):
        super(AddEventForm, self).__init__(*args, **kwargs)
        self.categories.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]

class AddUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(max=30)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=70)])
    submit = SubmitField('Add User')
            