from flask import render_template, request, flash, redirect, url_for
from models import db, Venue, Genre
from forms import VenueForm
from . import num_upcoming_shows, divide_shows, rt


genre_name = {g.id: g.description for g in Genre.query.order_by('id').all()}


@rt.route('/venues')
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
@rt.route('/venues/search', methods=['POST'])
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
@rt.route('/venues/<int:venue_id>', methods=['GET'])
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
@rt.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

# works well!
@rt.route('/venues/create', methods=['POST'])
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
@rt.route('/venues/<venue_id>', methods=['DELETE'])
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


# Works Well
@rt.route('/venues/<int:venue_id>/edit', methods=['GET'])
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
@rt.route('/venues/<int:venue_id>/edit', methods=['POST'])
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
