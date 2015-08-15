# SteamID utility library
#
# Decoding based on original work discovered here:
#   https://forums.alliedmods.net/showthread.php?t=60899
#   http://www.wiki.no-tag.de/index.php?title=Convert_SteamID_to_CommunityID
#
# Important Terminology/Variables:
#   steam_id: String STEAM_0:X:XXXXXXXXXX format.
#   steam_64: Integer 64bit numeric (CommunityID/SteamID64) generally starting
#     with 76561197960...
#   steam_vanity: String current Steam username (VanityID/FriendID)
#     Steam API: http://wiki.teamfortress.com/wiki/WebAPI/ResolveVanityURL
#   STEAM_RESERVED: Integer 64bit binary number for calculating IDs. Binary
#     representation of this number allows steam to set additional flags in the
#     future, like IP subnett/masking.
#
STEAM_RESERVED = 76561197960265728

class SteamIdError(Exception):
  """Base exception for Steam ID errors."""

def ToSteamId(steam_64):
  """Returns string representing the SteamId.
  
  Requires:
    steam_64: Integer 64bit representing the Steam ID.
  
  Returns:
    String steam_id.

  Raises:
    SteamIdError on validation errors.
  """
  if not isinstance(steam_64, int):
    raise SteamIdError('SteamID64 must be a 64bit integer.')
  auth_server = 0
  auth_removed_steam_64_id = steam_64
  if steam_64 % 2 != 0:
    auth_server = 1
    auth_removed_steam_64_id -= 1
  user_id = (auth_removed_steam_64_id - STEAM_RESERVED) / 2
  return 'STEAM_0:%s:%s' % (auth_server, user_id)

def ToSteam64(steam_id):
  """Returns steam_64 from a steam_id.

  Requires:
    steam_id: String in the format: STEAM_0:X:XXXXXXXXXX

  Returns:
    Integer SteamId64 representation.
  """
  if not isinstance(steam_id, (str, unicode)):
    raise SteamIdError('SteamID must be a string.')
  try:
    header, auth_server, user_id = steam_id.split(':', 2)
    steam_64 = (int(user_id) * 2) + int(auth_server) + STEAM_RESERVED
  except (ValueError, TypeError), e:
    raise SteamIdError('SteamID format invalid. Must be: STEAM_0:X:XXXXXXXXXX')
  return steam_64

def ConvertSteamProfileUrl(url):
  """Converts a given Steam profile URL

  Assumes input has been properly escaped.

  steamcommunity.com/id/<username>
  steamcommunity.com/profile/<steam_64>

  Requires:
    url: String URL of profile to parse.

  Returns:
    Integer 64bit steam_64 ID; or String Steam Vanity Username.
  """
  if 'steamcommunity.com/' not in url:
    raise SteamIdError('Invalid Steam profile URL: %s' % url)
  stripped_whack = url.rstrip('/')
  url_data = stripped_whack[stripped_whack.rfind('/') + 1:]
  if '/id/' in url:
    return url_data
  if '/profile/' in url:
    try:
      return int(url_data)
    except ValueError:
      raise SteamIdError('Steam /profile/ urls must be Integers. %s' % url)
  raise SteamIdError('Unknown Steam profile URL: %s' % url)

