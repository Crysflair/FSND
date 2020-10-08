from shared import db

venue_genre = db.Table(
    'venue_genre',
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True),
)

artist_genre = db.Table(
    'artist_genre',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True),
)

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(100))

    def __repr__(self):
        return f"<Genre id={self.id} description={self.description}>"


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
    genres = db.relationship('Genre', secondary=venue_genre, backref='venues', lazy=True)
    shows = db.relationship('Show', backref='venue', cascade=['all'], lazy=True)

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name}>"

    def venue_to_dictionary(self):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "genres": [g.description for g in sorted(self.genres, key=lambda a: a.id)]
        }
        return data



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
    genres = db.relationship('Genre', secondary=artist_genre, backref='artists', lazy=True)
    shows = db.relationship('Show', backref='artist', cascade=['all'], lazy=True)

    def __repr__(self):
        return f"<Artist id={self.id} name={self.name}>"

    def artist_to_dictionary(self):
        data = {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "genres": [g.description for g in sorted(self.genres, key=lambda a: a.id)]
        }
        return data



class Show(db.Model):
    __tablename__ = 'shows'
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)

    def __repr__(self):
        return f"<Show artist={self.artist.id} venue={self.venue.id} " \
               f"start_time={self.start_time.isoformat()}> "

