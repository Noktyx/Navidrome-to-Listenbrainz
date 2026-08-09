from typing import NamedTuple


class Scrobble(NamedTuple):
	submission_time: int|None
	artist: str
	album: str
	title: str
	musicbrainz_id: int|None

class Favourite(NamedTuple):
	artist: str
	title: str
	musicbrainz_id: str


# -------- https://listenbrainz.readthedocs.io/en/latest/users/json.html --------
class AdditionalInfo(NamedTuple):
	recording_mbid: str|int

class TrackMetadata(NamedTuple):
	artist_name: str
	track_name: str
	release_name: str
	additional_info: AdditionalInfo|None

class Listen(NamedTuple):
	listened_at: int
	track_metadata: TrackMetadata
# -------------------------------------------------------------------------------


FETCH_SCROBBLES: str = """
	SELECT scrobbles.submission_time, media_file.artist, media_file.album, media_file.title, media_file.mbz_recording_id
	FROM scrobbles
	JOIN media_file ON scrobbles.media_file_id = media_file.id
	ORDER BY scrobbles.submission_time
"""

FETCH_FAVOURITES: str = """
	SELECT media_file.artist, media_file.title, media_file.mbz_recording_id
	FROM annotation
	JOIN media_file ON annotation.item_id = media_file.id
	WHERE annotation.starred = 1 AND annotation.item_type = 'media_file'
	ORDER BY annotation.starred_at
"""

# -----------------------------------------------------------------------------------
# NAVIDROME DATABASE TABLES:														|
# 																					|
# album, album_artists, artist, *media_file, media_file_artists						|
# *scrobbles, *annotation, playlist, playqueue										|
# user, library, user_props, user_library											|
# folder, tag, library_artist, library_tag, radio, share							|
# bookmark, player, transcoding														|
# playlist_fields, playlist_tracks													|
# scrobble_buffer																	|
# property, plugin, goose_db_version												|
# album_fts, album_fts_config, album_fts_data, album_fts_idx						|
# artist_fts, artist_fts_config, artist_fts_data, artist_fts_idx					|
# media_file_fts, media_file_fts_config, media_file_fts_data,						|
# media_file_fts_docsize, media_file_fts_idx										|
# -----------------------------------------------------------------------------------
# 'annotation' TABLE SCHEMA:														|
# 																					|
# user_id, item_id, *item_type														|
# play_count, play_date																|
# rating, *starred, *starred_at, rated_at											|
# -----------------------------------------------------------------------------------
# 'media_file' TABLE SCHEMA:														|
# 																					|
# path, *title, *album, *artist, artist_id, album_artist, album_id					|
# has_cover_art, track_number, disc_number, year, size, suffix						|
# duration, bit_rate, genre, compilation											|
# created_at, updated_at, full_text													|
# album_artist_id, date, original_year, original_date								|
# release_year, release_date														|
# order_album_name, order_album_artist_name, order_artist_name						|
# sort_album_name, sort_artist_name, sort_album_artist_name, sort_title				|
# disc_subtitle, catalog_num, comment, order_title									|
# *mbz_recording_id, mbz_album_id, mbz_artist_id, mbz_album_artist_id				|
# mbz_album_type, mbz_album_comment, mbz_release_track_id							|
# channels, lyrics, sample_rate, library_id											|
# ----------------------------------------------------------------------------------|
# 'scrobbles' TABLE SCHEMA:															|
# 																					|
# *media_file_id, user_id, *submission_time											|
# -----------------------------------------------------------------------------------

# Hail thee, unknown soul!
