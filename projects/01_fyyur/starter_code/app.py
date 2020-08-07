# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, make_response, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler



# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
mig = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

venue_genre = db.Table(
    'venue_genre',
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True),
)

artist_genre = db.Table(
    'artist_genre',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True),
)


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(10))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    genres = db.relationship('Genre', secondary=venue_genre, backref='venues', cascade=['all'], lazy=True)
    shows = db.relationship('Show', backref='venue', cascade=['all'], lazy=True)

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name}>"


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(10))
    phone = db.Column(db.String(30))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    genres = db.relationship('Genre', secondary=artist_genre, backref='artists', cascade=['all'], lazy=True)
    shows = db.relationship('Show', backref='artist', cascade=['all'], lazy=True)

    def __repr__(self):
        return f"<Artist id={self.id} name={self.name}>"


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(100))

    def __repr__(self):
        return f"<Genre id={self.id} description={self.description}>"


class Show(db.Model):
    __tablename__ = 'shows'
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)

    def __repr__(self):
        return f"<Show artist={self.artist.id} venue={self.venue.id} " \
               f"start_time={self.start_time.isoformat()}> "


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        f = "EEEE MMMM, d, y 'at' h:mm a"
    elif format == 'medium':
        f = "EE MM, dd, y h:mm a"
    else:
        f = 'short'
    return babel.dates.format_datetime(date, format=f, locale='en_US')


app.jinja_env.filters['datetime'] = format_datetime

# ----------
# Helper
# ----------

def divide_shows(shows):
    past = [s for s in shows if s.start_time < datetime.now()]
    upcoming = [s for s in shows if s.start_time >= datetime.now()]
    return past, upcoming

def num_upcoming_shows(shows):
    return len(divide_shows(shows)[1])


genre_name = {g.id: g.description for g in Genre.query.order_by('id').all()}
# so that forms can import genre_name from app.
import forms
forms.genre_name = genre_name
from forms import *



# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/', methods=['GET', 'DELETE'])
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------


# Works well!
@app.route('/venues')
def venues():
    city_state = db.session.query(Venue.city, Venue.state).distinct().all()
    data = []
    for city, state in city_state:
        tmp = {"city": city, "state": state, "venues": []}
        for vn in Venue.query.filter_by(city=city, state=state).all():
            tmp['venues'].append({
                "id": vn.id, "name": vn.name,
                "num_upcoming_shows": num_upcoming_shows(vn.shows)
            })
        data.append(tmp)
    return render_template('pages/venues.html', areas=data)

# Works well!
@app.route('/venues/search', methods=['POST'])
def search_venues():
    # case-insensitive search
    tag = request.form['search_term']   # not sure how is the key defined.
    search = "%{}%".format(tag)
    result = Venue.query.filter(Venue.name.ilike(search)).all()
    response = {
        "count": len(result),
        "data": [{
            "id": vn.id, "name": vn.name,
            "num_upcoming_shows": num_upcoming_shows(vn.shows)
        } for vn in result]
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


# works well!
@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    vn = Venue.query.get(venue_id)
    past, upcoming = divide_shows(vn.shows)
    past_shows = [{
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat(),
    } for show in past]
    upcoming_shows = [{
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat()
    } for show in upcoming]
    data = {
        "id": vn.id,
        "name": vn.name,
        "genres": [genre_name[g.id] for g in vn.genres],
        "address": vn.address,
        "city": vn.city,
        "state": vn.state,
        "phone": vn.phone,
        "website": vn.website,
        "facebook_link": vn.facebook_link,
        "seeking_talent": vn.seeking_talent,
        "seeking_description": vn.seeking_description,
        "image_link": vn.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

# works well!
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

# works well!
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    success = True
    error_msg = ''
    try:
        f = request.form
        vf = VenueForm(f)
        if not vf.validate():
            success = False
            for key,val in vf.errors.items():
                error_msg += key + ": " + ';'.join(val) + "\n"
        else:
            g_ids = [int(i) for i in f.getlist('genres')]
            vn = Venue(name=f['name'], city=f['city'], state=f['state'], address=f['address'],
                       phone=f['phone'], facebook_link=f['facebook_link'],
                       genres=db.session.query(Genre).filter(Genre.id.in_(g_ids)).all(),
                       image_link=f['image_link'], website=f['website'],
                       seeking_talent=('seeking_talent' in f), seeking_description=f['seeking_description'],
                       )
            db.session.add(vn)
            db.session.commit()
    except:
        db.session.rollback()
        success = False
    finally:
        db.session.close()

    if success:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.' + error_msg)
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

# Works with problems.
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue_id = int(venue_id)
    success = True
    vn = Venue.query.get(venue_id)
    name = vn.name if vn is not None else ''
    try:
        db.session.delete(vn)
        db.session.commit()
    except:
        db.session.rollback()
        success = False
    finally:
        db.session.close()

    # FIXME This does not work!
    if success:
        flash('Venue ' + name + ' was successfully deleted!')
    else:
        flash('An error occurred. This venue could not be deleted.')

    return render_template('pages/home.html')
    #return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------

# Works well!
@app.route('/artists')
def artists():
    data = [{
        "id": a.id,
        "name": a.name,
    } for a in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)

# Works well!
@app.route('/artists/search', methods=['POST'])
def search_artists():
    tag = request.form['search_term']  # not sure how is the key defined.
    search = "%{}%".format(tag)
    result = Artist.query.filter(Artist.name.ilike(search)).all()
    response = {
        "count": len(result),
        "data": [{
            "id": a.id, "name": a.name,
            "num_upcoming_shows": num_upcoming_shows(a.shows)
        } for a in result]
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))

# Works well! TODO should be the image link of the VENUE!!
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    at = Artist.query.get(artist_id)
    past, upcoming = divide_shows(at.shows)
    past_shows = [{
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat(),
    } for show in past]
    upcoming_shows = [{
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat(),
    } for show in upcoming]
    data = {
        "id": at.id,
        "name": at.name,
        "genres": [genre_name[g.id] for g in at.genres],
        "city": at.city,
        "state": at.state,
        "phone": at.phone,
        "website": at.website,
        "facebook_link": at.facebook_link,
        "seeking_venue": at.seeking_venue,
        "seeking_description": at.seeking_description,
        "image_link": at.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artists(artist_id):
    success = True
    at = Artist.query.get(artist_id)
    name = at.name if at is not None else ''
    try:
        db.session.delete(at)
        db.session.commit()
    except:
        db.session.rollback()
        success = False
    finally:
        db.session.close()

    # FIXME This does not work!
    if success:
        flash('Artist ' + name + ' was successfully deleted!')
        #res = make_response(jsonify({}), 204)
        #return res
        return render_template('pages/home.html')
    else:
        flash('An error occurred. This artist could not be deleted.')
        res = make_response(jsonify({"error": "Fail to delete"}), 400)
        return res




#  Update
#  ----------------------------------------------------------------

# Works Well
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    at = Artist.query.get(artist_id)
    artist = {
        "id": at.id,
        "name": at.name,
        "city": at.city,
        "state": at.state,
        "phone": at.phone,
        "website": at.website,
        "facebook_link": at.facebook_link,
        "seeking_venue": at.seeking_venue,
        "seeking_description": at.seeking_description,
        "image_link": at.image_link,
        "genres": [g.id for g in at.genres]
    }
    form = ArtistForm(**artist)
    error_msg = ''
    form.validate()
    for key,val in form.errors.items():
        if key != 'csrf_token':
            error_msg += key + ": " + ';'.join(val)
    if error_msg:
        flash('There are few errors in the old artist info. Please fix them first! ' + error_msg)

    return render_template('forms/edit_artist.html', form=form, artist=artist)

# Works Well!
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    success = True
    error_msg = ''
    try:
        f = request.form
        af = ArtistForm(f)
        if not af.validate():
            success = False
            for key,val in af.errors.items():
                error_msg += key + ": " + ';'.join(val)
        else:
            at = Artist.query.get(artist_id)
            at.name = f["name"]
            at.city = f["city"]
            at.state = f["state"]
            at.phone = f["phone"]
            at.facebook_link = f["facebook_link"]
            at.website = f["website"]
            at.image_link = f["image_link"]
            at.seeking_venue = bool('seeking_venue' in f)
            at.seeking_description = f['seeking_description']
            g_ids = [int(i) for i in f.getlist('genres')]
            at.genres = db.session.query(Genre).filter(Genre.id.in_(g_ids)).all()
            db.session.commit()
    except:
        success = False
        db.session.rollback()
    finally:
        db.session.close()

    if success:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    else:
        flash('An error occurred. Artist' + request.form['name'] + ' could not be updated.' + error_msg)

    return redirect(url_for('show_artist', artist_id=artist_id))

# Works Well
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    vn = Venue.query.get(venue_id)
    venue = {
        "id": vn.id,
        "name": vn.name,
        "address": vn.address,
        "city": vn.city,
        "state": vn.state,
        "phone": vn.phone,
        "website": vn.website,
        "facebook_link": vn.facebook_link,
        "seeking_talent": vn.seeking_talent,
        "seeking_description": vn.seeking_description,
        "image_link": vn.image_link,
        "genres": [g.id for g in vn.genres]
    }
    form = VenueForm(**venue)
    error_msg = ''
    form.validate()
    for key,val in form.errors.items():
        if key != 'csrf_token':
            error_msg += key + ": " + ';'.join(val)
    if error_msg:
        flash('There are few errors in the old venue info. Please fix them first! ' + error_msg)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

# Works Well
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    success = True
    error_msg = ''

    try:
        f = request.form
        rf = VenueForm(request.form)
        if not rf.validate():
            success = False
            for key, val in rf.errors.items():
                error_msg += key + ": " + ';'.join(val)
        else:
            vn = Venue.query.get(venue_id)
            vn.name = f["name"]
            vn.city = f["city"]
            vn.state = f["state"]
            vn.address = f["address"]
            vn.phone = f["phone"]
            vn.image_link = f["image_link"]
            vn.facebook_link = f["facebook_link"]
            g_ids = [int(i) for i in f.getlist('genres')]
            vn.website = f['website']
            vn.seeking_talent = "seeking_talent" in f
            vn.seeking_description = f["seeking_description"]
            vn.genres = db.session.query(Genre).filter(Genre.id.in_(g_ids)).all()
            db.session.commit()
    except:
        success = False
        db.session.rollback()
    finally:
        db.session.close()

    if success:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.'+error_msg)

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

# Works Well!
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    success = True
    error_msg = ''
    try:
        f = request.form
        af = ArtistForm(request.form)
        if not af.validate():
            success = False
            for key, val in af.errors.items():
                error_msg += key + ": " + ';'.join(val)
        else:
            g_ids = [int(i) for i in f.getlist('genres')]
            at = Artist(name=f["name"], city=f['city'], state=f['state'],
                        phone=f['phone'], facebook_link=f['facebook_link'],
                        genres=db.session.query(Genre).filter(Genre.id.in_(g_ids)).all(),
                        image_link=f['image_link'], website=f['website'],
                        seeking_venue=('seeking_venue' in f), seeking_description=f['seeking_description'],
                        )
            db.session.add(at)
            db.session.commit()
    except:
        db.session.rollback()
        success = False
    finally:
        db.session.close()

    if success:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.'+error_msg)

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

# Works Well!
@app.route('/shows')
def shows():
    data = [{
        "venue_id": sh.venue_id,
        "venue_name": sh.venue.name,
        "artist_id": sh.artist_id,
        "artist_name": sh.artist.name,
        "artist_image_link": sh.artist.image_link,
        "start_time": sh.start_time.isoformat(),
    } for sh in Show.query.all()]
    return render_template('pages/shows.html', shows=data)

# Works Well!
@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


# Works Well!
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    success = True
    error_msg = ''
    try:
        f = request.form
        sf = ShowForm(f)
        if not sf.validate():
            success = False
            for key,val in sf.errors.items():
                error_msg += key + ": " + ';'.join(val) + " \n"
        else:
            # check accessibility
            at = Artist.query.get(int(f["artist_id"]))
            vn = Venue.query.get(int(f["venue_id"]))
            if at is None or vn is None:
                success = False
                error_msg += " Invalid artist or venue ID! "
            else:
                if not at.seeking_venue or not vn.seeking_talent:
                    success = False
                    error_msg += " The artist or venue is not available. "
                else:
                    # create show
                    sh = Show(artist_id=int(f["artist_id"]), venue_id=int(f["venue_id"]),
                              start_time=dateutil.parser.parse(f["start_time"])
                              )
                    db.session.add(sh)
                    db.session.commit()
    except:
        success = False
        db.session.rollback()
    finally:
        db.session.close()

    if success:
        flash('Show was successfully listed!')
    else:
        flash('An error occurred. Show could not be listed. '+error_msg)

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
