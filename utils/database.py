import os, random
import sqlite3
from datetime import datetime
from typing import Any

import utils.queries as queries
from utils.helpers import ask_yes_no, validate_date, namedtuple_to_dict


def verify_database(db_path: str) -> bool:
	"""Checks whether the database is both accessible and usable.

	Args:
		db_filepath (str): The filepath of the database file.

	Returns:
		bool: 'True' if both conditions are met, 'False' otherwise.
	"""

	if (not os.path.exists(db_path)):
		return (False)

	try:
		connection: sqlite3.Connection = sqlite3.connect(db_path)
		connection.close()
		return (True)

	except sqlite3.DatabaseError:
		return (False)


def do_listens(scrobble_rows: list[queries.Scrobble]) -> list[dict[str, Any]]|None:
	"""
	Builds the actual final ListenBrainz JSON payload out of the given scrobbles.

	Args:
		scrobble_rows (list[queries.Scrobble]): The scrobbles.

	Returns:
		list[dict[str, Any]]|None: The formatted scrobbles if the user didn't leave the inputs, 'None' otherwise.
	"""

	# Check for missing timestamps
	missing_timestamp_rows: list[queries.Scrobble] = [scrobble_row for scrobble_row in scrobble_rows if (not scrobble_row.submission_time)]
	length_missing_timestamp_rows: int = len(missing_timestamp_rows)
	length_scrobble_rows: int = len(scrobble_rows)

	print(f"\n{length_scrobble_rows} plays total, of which {length_missing_timestamp_rows} \
({(((len(missing_timestamp_rows) / length_scrobble_rows) * 100) if (scrobble_rows) else 0.00):.2f}% of the total) \
{"is" if (length_missing_timestamp_rows == 1) else "are"} missing a timestamp.")

	if ((missing_timestamp_rows) and (ask_yes_no("Show a list of the songs missing a timestamp?"))):
		for (index, row) in enumerate(missing_timestamp_rows, start=1):
			print(f"{index}. {row.artist} - \"{row.title}\"")


	# Randomise dates (If the user decides to)
	should_randomise: bool = False

	if ((missing_timestamp_rows) and (ask_yes_no("\nRandomise dates to import these tracks anyway? (Choosing 'n' will exclude them)"))):
		should_randomise: bool = True

		while (True):
			start_date: str = input("Start date [YYYY-MM-DD] (or 'exit' to not import listens): ").strip()
			if (start_date.lower() == "exit"): return (None)
			elif (validate_date(start_date)): break

		while (True):
			end_date: str = input("End date [YYYY-MM-DD] (or 'exit' to quit): ").strip()
			if (end_date.lower() == "exit"): return (None)
			elif (validate_date(end_date)): break

		randomise_start_timestamp: int = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
		randomise_end_timestamp: int = int(datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=42).timestamp())


	# Format listens for ListenBrainz API
	formatted_listens: list[dict[str, Any]] = []

	for scrobble_row in scrobble_rows:
		listen_timestamp: int|None = scrobble_row.submission_time
		if (listen_timestamp is None):
			if (not should_randomise): continue  # Cannot submit a listen without a timestamp!
			listen_timestamp = random.randint(randomise_start_timestamp, randomise_end_timestamp) #type: ignore[arg-type]

		additional_info: queries.AdditionalInfo|None = queries.AdditionalInfo(recording_mbid=scrobble_row.musicbrainz_id) if (scrobble_row.musicbrainz_id) else None

		track_metadata: queries.TrackMetadata = queries.TrackMetadata(
			artist_name=scrobble_row.artist,
			track_name=scrobble_row.title,
			release_name=scrobble_row.album,
			additional_info=additional_info
		)

		listen_obj: queries.Listen = queries.Listen(listened_at=listen_timestamp, track_metadata=track_metadata)
		formatted_listens.append(namedtuple_to_dict(listen_obj))

	return (formatted_listens)


def do_favourites(favourite_rows: list[queries.Favourite]) -> list[queries.Favourite]|None:
	"""
	Filters the given favourites from the ones that cannot actually be submitted (i.e., have a MusicBrainz ID).
	Unlike the function 'do_listens', no conversion to dict will be done, since the function 'submit_like_wrapper' 
	builds the API payload directly from the Favourite's attributes because of how simple it is.

	Args:
		favourite_rows (list[Favourite]): The favourites (feedback).

	Returns:
		list[queries.Favourite]|None: The favourites if the user didn't leave the inputs, 'None' otherwise.
	"""

	# Check for missing MusicBrainz IDs
	rows_with_mbid: list[queries.Favourite] = [favourite_row for favourite_row in favourite_rows if (favourite_row.musicbrainz_id)]
	rows_without_mbid: list[queries.Favourite] = [favourite_row for favourite_row in favourite_rows if (not favourite_row.musicbrainz_id)]
	length_favourite_rows: int = len(favourite_rows)
	length_rows_without_mbid: int = len(rows_without_mbid)

	print(f"\n{length_favourite_rows} favourites total, of which {length_rows_without_mbid} \
({(((length_rows_without_mbid / length_favourite_rows) * 100) if (favourite_rows) else 0.00):.2f}% of the total) \
{"doesn't" if (length_rows_without_mbid == 1) else "don't"} have a MusicBrainz ID.")


	if (not rows_without_mbid):
		if (ask_yes_no("Proceed?")): return (rows_with_mbid)


	print("These cannot be submitted unless you add their respective MusicBrainz ID.")
	if ((rows_without_mbid) and (ask_yes_no("\nShow the ones missing a MusicBrainz id?"))):
		print("\nInvalid favourites: ")
		for (index, row) in enumerate(rows_without_mbid, start=1):
			print(f"{index}. {row.artist} - \"{row.title}\"")

	print("\n")
	if (not ask_yes_no("Proceed with submitting the remaining favourites?")):
		return (None)

	return (rows_with_mbid)
