from config import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_description = db.Column(db.String(120),nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    show = db.relationship("Show", backref="venue", lazy="joined", cascade="all, delete")

    def __repr__(self):
      return f'<Venue ID:{self.id} name: {self.name} city:{self.city} state:{self.state} address:{self.address} phone:{self.phone} seeking_talent:{self.seeking_talent} seeking_description:{self.seeking_description} genres:{self.genres}'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=True)
    seeking_description = db.Column(db.String(120), nullable=True)
    show = db.relationship("Show", backref="artist", lazy="joined", cascade="all, delete")

    def __repr__(self):
      return f'<Artist ID:{self.id} name: {self.name} city:{self.facebook_link} state:{self.state} phone:{self.phone} genres:{self.genres} image:{self.image_link} facebook:{self.facebook_link}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=True)
    start_time= db.Column(db.DateTime(), nullable=True)
    
    def __repr__(self):
      return f'<Show ID:{self.id} time:{self.start_time}>'