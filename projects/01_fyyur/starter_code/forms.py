from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField, SelectMultipleField,
    DateTimeField,
    BooleanField,
    TextAreaField
)
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, ValidationError, Optional
from shared import genre_choice


# Constants

state_choices = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

# Define Forms



def ifArtistExists(form, field):
    from models import Artist
    if Artist.query.get(field.data) is None:
        raise ValidationError('Artist not listed in our database')

def ifVenueExists(form, field):
    from models import Venue
    if Venue.query.get(field.data) is None:
        raise ValidationError('Artist not listed in our database')


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired(), ifArtistExists]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired(), ifVenueExists]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[
            DataRequired(),
            Regexp(r'^[1-9][0-9]{2}-[0-9]{3}-[0-9]{4}$',
                   message='Wrong phone number format!')]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genre_choice, coerce=int
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
    )
    website = StringField(
        'website', validators=[Optional(), URL()]
    )

    seeking_talent = BooleanField(
        'seeking_talent', default=False   # validators=[DataRequired()] This causes 'False' value invalid.
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )


class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    phone = StringField(
        'phone', validators=[
            DataRequired(),
            Regexp(r'^[1-9][0-9]{2}-[0-9]{3}-[0-9]{4}$',
                   message='Wrong phone number format!')]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genre_choice, coerce=int
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(),URL()]
    )
    website = StringField(
        'website', validators=[Optional(), URL()]
    )
    seeking_venue = BooleanField(
        'seeking_venue', default=False
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )