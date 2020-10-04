
from flask import render_template, request, flash
from models import db, Show, Artist, Venue
from forms import ShowForm
import dateutil.parser
from . import rt


# Works Well!
@rt.route('/shows')
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
@rt.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


# Works Well!
@rt.route('/shows/create', methods=['POST'])
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
