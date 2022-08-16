from models import Venue, Artist, Show



def shows_decorator(shows):
    """
      Iterates the list of objects and picks out related artists and venues.
    """
    data = []
    for show in shows:
      artist = Artist.query.get(show.artist_id)
      venue = Venue.query.get(show.venue_id)
      data.append({
        "artist_id": show.artist_id,
        "venue_id": show.venue_id,
        "artist_name": artist.name,
        "venue_name": venue.name,
        "artist_image_link": artist.image_link,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)
      })
    return data
