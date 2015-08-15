# Generic Steam API interface for PD2 Cheater Confidence.

import simplejson
import urllib
import urllib2


class SteamApiError(Exception):
  """Base exception for Steam API errors."""

class SteamApi(object):
  """Object containing simplified methods for accessing the Steam API.
  
  Attributes:
    api_key: Tuple containing Steam Dev API Key-value pair.
    
  """
  API_BASE = 'http://api.steampowered.com/'
  
  def __init__(self, api_key):
    """Initializes steam API object.
    
    Requires:
      api_key: String Steam API key for accessing API.
    """
    self.base_api_data = {
      'appid': '218620',
      'key': api_key}
      
  def GetPd2Stats(self, steam_64):
    """Returns a JSON object containing PD2 Stat information.
    
    Requires:
      steam_64: Integer Steam64ID to look up.
    
    Returns:
      JSON object containing parsed information.
    
    Raises:
      SteamApiError containing debug information.
    """
    return self._QuerySteamApi('ISteamUserStats/GetUserStatsForGame/v0002',
                               {'steamid': steam_64})

  def ResolveSteamVanity(self, username):
    """Resolves a Steam Vanity username to steam_64.

    http://wiki.teamfortress.com/wiki/WebAPI/ResolveVanityURL

    'success': 1 if successful, 42 no match
    'steamid': 64 bit SteamId. Nothing on failures
    'message': String failure message if failed.

    Requires:
      String: Steam vanity username to resolve.

    Returns:
      Integer SteamId64 (steam_64).

    Raises:
      SteamApiError containing debug information.
    """
    results = self._QuerySteamApi('ISteamUser/ResolveVanityURL/v0001',
                                  {'vanityurl': username}, auth_both=False)
    
    if results['response']['success'] != 1:
      raise SteamApiError(results['response']['message'])
    return int(results['response']['steamid'])

  def _SteamQueryBuilder(self, query, query_args=None, auth_both=True):
    """Build a query URI for Steam API, forcing GET method.

    urllib2.urlopen only uses get if data=None, meaning that queryargs must be
    pre-encoded for the URL. This method does this.

    Requires:
      query: String API URL to use.
      query_args: Dictionary url query data to use.
      auth_both: Boolean True to auth with api_key/appid, False just api_key.

    Returns:
      String URI ready for use with Steam API.
    """
    if query_args is None:
      query_args = {}
    if auth_both:
      query_args.update(self.base_api_data)
    else:
      query_args.update({'key': self.base_api_data['key']})
    return '%s%s/?%s' % (self.API_BASE, query, urllib.urlencode(query_args))
  
  def _QuerySteamApi(self, query, url_data, auth_both=True):
    """Generic query mechanism to return JSON data.
    
    Steam API requires data to be in specific a order.
    
    Requires:
      query: String API URL to use.
      url_data: Dictionary url query data to use.
      auth_both: Boolean True to auth with api_key/appid, False just api_key.
    
    Returns:
      JSON object containing parsed information.
    
    Raises:
      SteamApiError containing debug information.
    """
    try:
      return simplejson.load(urllib2.urlopen(
          self._SteamQueryBuilder(query, url_data), timeout=10))
    except urllib2.URLError, e:
      raise SteamApiError(e)
    except simplejson.JSONDecodeError, e:
      raise SteamApiError(e)
