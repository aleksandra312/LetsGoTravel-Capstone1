"""Forms for letsgotravel."""

from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange, Email, Optional
from flask_wtf import FlaskForm


class BucketlistForm(FlaskForm):
    """Form for adding bucketlists."""

    name = StringField(
        "Name",
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    description = StringField(
        "Description",
        validators=[Length(min=1, max=50)]
    )
    
class SelectBucketlistForm(FlaskForm):
    """Form for selecting a bucketlist."""

    bucketlist = SelectField('Select a bucketlist', coerce=int)    
    

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6, max=55)],
    )
    
    
class RegisterForm(FlaskForm):
    """User registration form."""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6, max=55)],
    )
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)],
    )
    image_url = StringField('(Optional) Image URL')


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField(
        'Username', 
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6, max=55)],
    )
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)],
    )
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('(Optional) Tell us about yourself')
    location = StringField('(Optional) Location')
