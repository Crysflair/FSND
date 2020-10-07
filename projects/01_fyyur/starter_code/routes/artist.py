import datetime

from flask import render_template, request, flash, make_response, jsonify, redirect, url_for
from models import Artist, Genre, Venue, Show
from shared import db, genre_name
from forms import ArtistForm
from . import divide_shows, num_upcoming_shows, rt



# Works well!
@rt.route('/artists')
def artists():
    data = [{
        "id": a.id,
        "name": a.name,
    } for a in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)

# Works well!
@rt.route('/artists/search', methods=['POST'])
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

# Works well!
@rt.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    at = Artist.query.get(artist_id)
    show_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id)
    upcoming = show_query.filter(Show.start_time >= datetime.datetime.now()).all()
    past = show_query.filter(Show.start_time < datetime.datetime.now()).all()

    upcoming_shows = [{
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat(),
    } for show in upcoming]

    # filling out the Venues page with a “Past Performances” section
    past_shows = [{
        "venue_id": show.venue_id,
        "venue_name": db.session.query(Venue).join(Show, show.venue_id==Venue.id).all()[0].name,
        "venue_image_link": db.session.query(Venue).join(Show).filter(show.venue_id==Venue.id).all()[0].image_link,
        "start_time": show.start_time.isoformat(),
    } for show in past]

    data = at.artist_to_dictionary()
    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


@rt.route('/artists/<int:artist_id>', methods=['DELETE'])
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
@rt.route('/artists/<int:artist_id>/edit', methods=['GET'])
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
@rt.route('/artists/<int:artist_id>/edit', methods=['POST'])
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

    return redirect(url_for('rt.show_artist', artist_id=artist_id))

# Works Well!
@rt.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@rt.route('/artists/create', methods=['POST'])
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

