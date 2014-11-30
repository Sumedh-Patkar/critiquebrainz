"""
This module provides functions that can help access Spotify Web API.

More information about it is available at https://developer.spotify.com/web-api/.
"""
import requests
import urllib
from critiquebrainz import cache

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)

BASE_URL = "https://api.spotify.com/v1"


def search(query, type, limit=20, offset=0):
    """Get Spotify catalog information about artists, albums, or tracks that match a keyword string.

    More information is available at https://developer.spotify.com/web-api/search-item/.
    """
    key = cache.generate_cache_key('search', source='spotify', params=[query, type, limit, offset])
    resp = cache.mc.get(key)
    if not resp:
        resp = requests.get("%s/search?q=%s&type=%s&limit=%s&offset=%s" %
                            (BASE_URL, urllib.quote(query.encode('utf8')), type, str(limit), str(offset))).json()
        cache.mc.set(key, resp, DEFAULT_CACHE_EXPIRATION)
    return resp


def get_album(spotify_id):
    """Get Spotify catalog information for a single album.

    Returns:
        Album object from Spotify. More info about this type of object is available at
        https://developer.spotify.com/web-api/object-model/#album-object.
    """
    key = cache.generate_cache_key('album', source='spotify', params=[spotify_id])
    resp = cache.mc.get(key)
    if not resp:
        resp = requests.get("%s/albums/%s" % (BASE_URL, spotify_id)).json()
        cache.mc.set(key, resp, DEFAULT_CACHE_EXPIRATION)
    return resp


def get_multiple_albums(spotify_ids):
    """Get Spotify catalog information for multiple albums identified by their Spotify IDs.

    Returns:
        List of album objects from Spotify. More info about this type of objects is available
        at https://developer.spotify.com/web-api/object-model/#album-object.
    """
    key = cache.generate_cache_key('albums', source='spotify', params=spotify_ids)
    resp = cache.mc.get(key)
    if not resp:
        resp = requests.get("%s/albums?ids=%s" % (BASE_URL, ','.join(spotify_ids))).json()['albums']
        cache.mc.set(key, resp, DEFAULT_CACHE_EXPIRATION)
    return resp
