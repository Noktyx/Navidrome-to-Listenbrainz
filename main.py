import sys, requests
import json, sqlite3
from typing import Final, Any

import utils.queries as queries
from utils.queries import FETCH_SCROBBLES, FETCH_FAVOURITES
from utils.helpers import ask_yes_no, clear_screen
from utils.listenbrainz_api import validate_token, submit_listens_batch_wrapper, submit_like, wait_for_rate_limit
from utils.database import verify_database, do_listens, do_favourites


def load_config(config_path: str = "config.json") -> dict:
	"""Loads configuration from the JSON file.

	Args:
		config_path (str, optional): The path of the configuration json file. Defaults to "config.json".

	Returns:
		dict: Configuration dictionary.
	"""

	try:
		with open(config_path, 'r') as file:
			return (json.load(file))

	except FileNotFoundError:
		print(f"Error: {config_path} not found. Exiting...")
		sys.exit(1)
		assert False

	except json.JSONDecodeError:
		print(f"Error: {config_path} is NOT a valid JSON. Exiting...")
		sys.exit(1)
		assert False

	except Exception as exception:
		print(f"Error: {exception}. Exiting...")
		assert False


def main() -> None:
	CONFIG: Final[dict] = load_config()

	DB_PATH: Final[str] = CONFIG['db_path']
	LISTENBRAINZ_VALIDATE_URL: Final[str] = CONFIG['listenbrainz_validate_url']
	LISTENBRAINZ_SUBMIT_URL: Final[str] = CONFIG['listenbrainz_submit_url']
	LISTENBRAINZ_FEEDBACK_URL: Final[str] = CONFIG['listenbrainz_feedback_url']
	MAX_SUBMIT_ATTEMPTS: Final[int] = CONFIG['max_submit_attempts']
	SECONDS_BEFORE_REATTEMPT: Final[int] = CONFIG['seconds_before_reattempt']


	if (not verify_database(DB_PATH)):
		print(f"Error: Database not found or corrupted at {DB_PATH}")
		sys.exit(1)


	while (True):
		token: str = input("Type your ListenBrainz token (or 'exit' to quit): ").strip()

		if (token.lower() == "exit"):
			print("Exiting...")
			return (None)

		print("Validating your token...")
		if (validate_token(LISTENBRAINZ_VALIDATE_URL, token)):
			print("Token is valid!\n")
			break

		clear_screen()
		print("Invalid token. Please try again.\n")


	# Listens ---
	if (ask_yes_no("Import your listens (listening history)?")):
		clear_screen()
		database_connection: sqlite3.Connection = sqlite3.connect(DB_PATH)
		scrobble_rows: list[queries.Scrobble] = [queries.Scrobble(*row) for row in database_connection.execute(FETCH_SCROBBLES).fetchall()]
		database_connection.close()

		formatted_listens: list[dict[str, Any]]|None = do_listens(scrobble_rows)

		if (formatted_listens != None):
			submit_listens_batch_wrapper(
				LISTENBRAINZ_SUBMIT_URL,
				token,
				formatted_listens,
				MAX_SUBMIT_ATTEMPTS,
				SECONDS_BEFORE_REATTEMPT
			)

		print("\n\nDone submitting listens.")


	# Favourites ---
	if (ask_yes_no("Import your favourites (feedback)?")):
		clear_screen()
		database_connection: sqlite3.Connection = sqlite3.connect(DB_PATH)
		favourite_rows: list[queries.Favourite] = [queries.Favourite(*row) for row in database_connection.execute(FETCH_FAVOURITES).fetchall()]
		database_connection.close()

		formatted_favourites: list[queries.Favourite]|None = do_favourites(favourite_rows)

		if (formatted_favourites): # != [] and != None
			print(f"Submitting {len(formatted_favourites)} feedbacks...")

			for count, favourite_row in enumerate(formatted_favourites, start=1):
				api_response: requests.Response = submit_like(LISTENBRAINZ_FEEDBACK_URL, token, favourite_row.musicbrainz_id)
				print(count, api_response.status_code, favourite_row.artist, "-", favourite_row.title)
				wait_for_rate_limit(api_response)
		else:
			print("No valid favourites (feedback) given.")


	print("\n---------------------------------\nDone! :]")



if (__name__ == "__main__"):
	main()
