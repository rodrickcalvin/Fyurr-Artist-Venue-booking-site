#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import (abort, render_template, request, flash, redirect, url_for)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from datetime import datetime
from models import *
from services.shows_decorators import shows_decorator


moment = Moment(app)
app.config.from_object('config')
db.init_app(app)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  --------------------------------------------------------------------------#
#  Display all venues according to the city and state
@app.route('/venues')
def venues():
    performance_venues = Venue.query.distinct(Venue.city, Venue.state).all()
    data = []

    for venue in performance_venues:
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [{
                "id": venue_data.id,
                "name": venue_data.name,
                "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue_data.id, Show.start_time > datetime.now()).all())
            } for venue_data in Venue.query.filter_by(city=venue.city, state=venue.state).all()]
        })
    print(data)

    return render_template('pages/venues.html', areas=data)


#  Venue Search
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(
        Venue.name.ilike("%{}%".format(search_term))).all()
    searched_venues = []
    for venue in venues:
        searched_venues.append({
            "id": venue.id,
            "name": venue.name,
        })
    response = {
        "count": len(venues),
        "data": searched_venues
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


#  View Specific Venue and related shows
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        past_shows = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
        upcoming_shows = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time >= datetime.now()).all()

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": shows_decorator(past_shows),
            "upcoming_shows": shows_decorator(upcoming_shows),
            "upcoming_shows_count": len(upcoming_shows),
            "past_shows_count": len(past_shows),
        }
    except:
        error = True
        print(sys.exc_info())
    if error == True:
        abort(500)
    else:
        return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  1------display empty venue form
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


#  2-------submit the data in the form
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    new_venue_form = VenueForm(request.form)
    error = False

    try:
        create_venue = Venue(
            name=new_venue_form.name.data,
            city=new_venue_form.city.data,
            state=new_venue_form.state.data,
            address=new_venue_form.address.data,
            phone=new_venue_form.phone.data,
            genres=new_venue_form.genres.data,
            facebook_link=new_venue_form.facebook_link.data,
            image_link=new_venue_form.image_link.data,
            website_link=new_venue_form.website_link.data,
            seeking_talent=new_venue_form.seeking_talent.data,
            seeking_description=new_venue_form.seeking_description.data
        )
        db.session.add(create_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/home.html')


#  Delete Venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("Venue {0} has been deleted successfully".format(
            venue[0]['name']))
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash("An error occurred. Venue {0} could not be deleted.".format(
            venue[0]['name']))
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        # display list of venues to show that the venue has been deleted
        # and nolonger in the list.
        return redirect(url_for('/venues'))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page,
    # have it so that clicking that button delete it from the db then redirect
    # the user to the homepage


#  Update/Edit Specific artist data
#  1------populate venue form with data from specific venue
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    get_venue = Venue.query.get(venue_id)

    venue = {
        "id": get_venue.id,
        "name": get_venue.name,
        "city": get_venue.city,
        "state": get_venue.state,
        "address": get_venue.address,
        "phone": get_venue.phone,
        "image_link": get_venue.image_link,
        "facebook_link": get_venue.facebook_link,
        "genres": get_venue.genres,
        "website_link": get_venue.website_link,
        "seeking_talent": get_venue.seeking_talent,
        "seeking_description": get_venue.seeking_description,

    }
    form = VenueForm(data=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


#  2------submit changes in data to specific venue id
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue_form = VenueForm(request.form)
    error = False

    try:
        venue = Artist.query.get(venue_id)

        venue.name = venue_form.name.data
        venue.city = venue_form.city.data
        venue.state = venue_form.state.data
        venue.address = venue_form.address.data
        venue.phone = venue_form.phone.data
        venue.image_link = venue_form.image_link
        venue.facebook_link = venue_form.facebook_link.data
        venue.genres = venue_form.genres.data   
        venue.website_link = venue_form.website_link.data
        venue.seeking_talent = venue_form.seeking_talent.data
        venue.seeking_description = venue_form.seeking_description.data,
        

        db.session.commit()
        flash('Venue ' + request.form['name'] +
                ' information was succesfully updated!')
    except:
        error = True
        db.session.rollback()
        flash('Venue ' + request.form['name'] +
                ' information was not updated!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  -------------------------------------------------------------------------#
#  Display all artists
@app.route('/artists')
def artists():
    artists = Artist.query.order_by('id').all()
    data = [{
        "id": artist.id,
        "name": artist.name
    } for artist in artists]

    return render_template('pages/artists.html', artists=data)


#  Artist Search
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_term))).all()
    searched_artists = [{
        "id": artist.id,
        "name": artist.name,
    } for artist in artists]
    response = {
        "count": len(artists),
        "data": searched_artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


#  View Specific Artist and related shows
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    error = False
    
    try:
        artist = Artist.query.get(artist_id)
        past_shows = db.session.query(Show).join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
        upcoming_shows = db.session.query(Show).join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time >= datetime.now()).all()

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": shows_decorator(past_shows),
            "upcoming_shows": shows_decorator(upcoming_shows),
            "upcoming_shows_count": len(upcoming_shows),
            "past_shows_count": len(past_shows),
        }

    except:
        error = True
        print(sys.exc_info())
    if error == True:
        abort(500)
    else:
        return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  1------display empty artist form
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


#  2------submit data in the artist form
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    new_artist_form = ArtistForm(request.form)
    error = False

    try:
        new_artist = Artist(
            name=new_artist_form.name.data,
            city=new_artist_form.city.data,
            state=new_artist_form.state.data,
            phone=new_artist_form.phone.data,
            image_link=new_artist_form.image_link.data,
            facebook_link=new_artist_form.facebook_link.data,
            genres=new_artist_form.genres.data,
            website_link=new_artist_form.website_link.data,
            seeking_venue=new_artist_form.seeking_venue.data,
            seeking_description=new_artist_form.seeking_description.data
        )

        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] +
                ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        flash('Artist ' + request.form['name'] + ' could not be listed!')

    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/home.html')


#  Update/Edit Specific artist data
#  1------populate artist form with data from specific artist
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    get_artist = Artist.query.get(artist_id)

    artist = {
        "id": get_artist.id,
        "name": get_artist.name,
        "city": get_artist.city,
        "state": get_artist.state,
        "phone": get_artist.phone,
        "image_link": get_artist.image_link,
        "facebook_link": get_artist.facebook_link,
        "genres": get_artist.genres,
        "website_link": get_artist.website_link,
        "seeking_venue": get_artist.seeking_venue,
        "seeking_description": get_artist.seeking_description,
    }
    form = ArtistForm(data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


#  2------submit changes in data to specific artist id
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist_form = ArtistForm(request.form)
    error = False

    try:
        artist = Artist.query.get(artist_id)

        artist.name = artist_form.name.data
        artist.city = artist_form.city.data
        artist.state = artist_form.state.data
        artist.phone = artist_form.phone.data
        artist.image_link = artist_form.image_link.data
        artist.facebook_link = artist_form.facebook_link.data
        artist.genres = artist_form.genres.data
        artist.website_link = artist_form.website_link.data
        artist.seeking_venue = artist_form.seeking_venue.data
        artist.seeking_description = artist_form.seeking_description.data

        db.session.commit()
        flash('Artist ' + request.form['name'] +
                ' information was succesfully updated!')
    except:
        error = True
        db.session.rollback()
        flash('Artist ' + request.form['name'] +
                ' information was not updated!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


#  Delete Specific artist data


#  Shows
#  -------------------------------------------------------------------------#
#  Display all shows
@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = [{
        "venue_id": show.venue_id,
        "artist_id": show.artist_id,
        "start_time": str(show.start_time),
        "artist_name": Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "venue_name": Venue.query.get(show.venue_id).name,
    } for show in shows]

    print(data)
    return render_template('pages/shows.html', shows=data)


#  Create Show
#  1------display empty show form
@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

#  2------submit data in the show form
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show_form = ShowForm(request.form)
    error = False

    try:
        new_show = Show(
            artist_id=show_form.artist_id.data,
            venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )

        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/home.html')




#  Errors
#  -------------------------------------------------------------------------#
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500



# ----------------------------------------------------------------------------#
#  Launch.
# ----------------------------------------------------------------------------#


#  Settings
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')



#  Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
