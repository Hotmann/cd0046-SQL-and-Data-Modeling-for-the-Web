#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
from traceback import format_list
from wsgiref import validate
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request,
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_migrate import Migrate
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from config import app
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


# TODO: connect to a local postgresql database

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  venues = Venue.query.all()

  areas = Venue.query.distinct(Venue.state, Venue.city).all()

  data = []

  for area in areas:
    
    data.append({
      "city": area.city,
      "state": area.state, 
      "venues": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len([show for show in venue.show if show.start_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
      } for venue in venues if
          venue.city == area.city and venue.state == area.state]
      }) 
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term")

  venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike(f"%{search_term}%")).all()

  for venue in venues:
    upcoming_show = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S')).count()
    
    response={
    "count": len(venues),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcoming_show
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get_or_404(venue_id)
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  past_shows = []
  upcoming_shows = []

  for show in venue.show:
    ven_show = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    }

    if show.start_time <= current_time:
      past_shows.append(ven_show)
    else:
      upcoming_shows.append(ven_show)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": json.loads(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link":venue.image_link,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request)
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue = Venue()
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.genres= json.dumps(form.genres.data)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form.get("name")+ ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form.get("name")  + ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
    return render_template('pages/home.html')
  return render_template('forms/new_venue.html', form=form)
# on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('Venue' + venue.name + ' could not be deleted !')
  else:
    flash('Venue ' + venue.name + ' was successfully deleted !')
 
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term")

  artists = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(f"%{search_term}%")).all()
  for artist in artists:
    upcoming_show = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S')).count

    response={
      "count": len(artists),
      "data": [{
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": upcoming_show
      }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get_or_404(artist_id)
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  
  past_shows = []
  upcoming_shows = []

  for show in artist.show:
    art_show = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    }

    if show.start_time <= current_time:
      past_shows.append(art_show)
    else:
      upcoming_shows.append(art_show)

  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": json.loads(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get_or_404(artist_id)
  
  if form.validate():
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres= json.dumps(form.genres.data)
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Artist '+request.form['name']+' update was successful ')
    except:
      db.session.rollback()
      flash('Artist '+request.form['name']+' update was unsuccessful ')
      print(sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  venue=Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get_or_404(venue_id)

  if form.validate():
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.genres= json.dumps(form.genres.data)
      db.session.commit()
      flash('Venue '+request.form['name']+' update was successful ')
    except:
      db.session.rollback()
      flash(form.errors)
      flash('Venue '+request.form['name']+' update was unsuccessful ')
      print(sys.exc_info())
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  return render_template('forms/edit_venue.html', form=form, venue=venue)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist()
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres= json.dumps(form.genres.data)
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
    return render_template('pages/home.html')
  return render_template('forms/new_artist.html', form=form)

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.join(Venue, Artist).all()

  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm(request.form)
  try:
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data,
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
