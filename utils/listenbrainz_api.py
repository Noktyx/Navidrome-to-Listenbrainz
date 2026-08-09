import sys, time, requests
from typing import Any

import utils.queries as queries


def wait_for_rate_limit(api_response: requests.Response, buffer_seconds: int = 1) -> None:
	"""
	Sleeps if ran out of requests for the current rate limit window for ListenBrainz.
	More information on ListenBrainz's docs: https://listenbrainz.readthedocs.io/en/latest/users/api/index.html#rate-limiting

	Args:
		api_response (requests.Response): The API response.
		buffer_seconds (int, optional): A safety margin in seconds added to the rate limit reset time,
		because you just never know! Defaults to 1.
	"""

	remaining: int = int(api_response.headers.get("X-RateLimit-Remaining", 1))

	if (remaining == 0):
		seconds_before_reset: int = int(api_response.headers.get("X-RateLimit-Reset-In", 0))
		print(f"Rate limit reached; sleeping for {seconds_before_reset}+{buffer_seconds} seconds.")
		time.sleep(seconds_before_reset+buffer_seconds)

	return (None)


def validate_token(listenbrainz_validate_url: str, token: str) -> bool:
	"""
	Validates a ListenBrainz token by hitting the ListenBrainz 'validate-token' endpoint.

	Args:
		listenbrainz_validate_url (str): The ListenBrainz validate-token endpoint.
		token (str): The ListenBrainz user token.

	Returns:
		bool: 'True' if the token is valid (and if no exception was raised), 'False' otherwise.
	"""

	try:
		api_response: requests.Response = requests.get(
			listenbrainz_validate_url,
			headers={"Authorization": f"Token {token}"}
		)
		return (api_response.json().get('valid') == True)

	except Exception as error:
		print(f"Error while validating token: {error}")
		sys.exit(1)


def submit_listens_batch(listenbrainz_submit_url: str, token: str, batch_data: list[dict[str, Any]]) -> requests.Response:
	"""
	Submits a batch of up to 1000 listens to ListenBrainz.

	Args:
		listenbrainz_submit_url (str): The ListenBrainz submit-listens endpoint.
		token (str): The ListenBrainz user token.
		batch_data (list[dict[str, Any]]): A batch of formatted listens.

	Returns:
		requests.Response: The API response.
	"""

	request_headers: dict[str, str] = {
		"Authorization": f"Token {token}",
		"Content-Type": "application/json"  #type/subtype
	}
	request_payload: dict[str, Any] = {
		"listen_type": "import",
		"payload": batch_data
	}

	try:
		return (requests.post(
			listenbrainz_submit_url,
			headers=request_headers,
			json=request_payload,
		))

	except Exception as exception:
		print(f"An exception was raised while attempting to send a request (to submit listens): {exception}")
		sys.exit(1)


def submit_listens_batch_wrapper(
	listenbrainz_submit_url: str,
	token: str,
	formatted_listens: list[dict[str, Any]],
	max_submit_attempts: int,
	seconds_before_reattempt: int
) -> None:
	"""
	Acts as a wrapper for the 'submit_listens_batch' function.

	Args:
		listenbrainz_submit_url (str): The ListenBrainz submit-listens endpoint.
		token (str): The ListenBrainz user token.
		formatted_listens (list[dict[str, Any]]): All formatted listens to submit.
		max_submit_attempts (int): Maximum number of submission attempts per batch.
		seconds_before_reattempt (int): Seconds to wait before retrying a failed batch.
	"""

	length_formatted_listens: int = len(formatted_listens)
	print(f"Submitting {length_formatted_listens} listens to ListenBrainz...")

	for batch_start_index in range(0, length_formatted_listens, 1000):
		batch_end_index: int = min((batch_start_index + 1000), length_formatted_listens)
		batch_data: list[dict[str, Any]] = formatted_listens[batch_start_index:batch_end_index]

		for attempt in range(0, max_submit_attempts):
			api_response: requests.Response = submit_listens_batch(listenbrainz_submit_url, token, batch_data)
			print(f"Batch ({batch_start_index} - {batch_end_index})'s status code: {api_response.status_code} ({attempt+1}° attempt)")

			if (api_response.ok):  #Code <400
				wait_for_rate_limit(api_response)
				break
			elif (attempt == (max_submit_attempts - 1)):
				print(f"Batch ({batch_start_index} - {batch_end_index}) aborted as {max_submit_attempts} attempts were reached.")
				break
			
			time.sleep(seconds_before_reattempt)

	return (None)


def submit_like(listenbrainz_feedback_url: str, token: str, musicbrainz_id: str) -> requests.Response:
	"""
	Submits a single "like" (feedback score of 1) for a recording.

	Args:
		listenbrainz_feedback_url (str): The ListenBrainz feedback endpoint.
		token (str): The ListenBrainz user token.
		musicbrainz_id (str): The MusicBrainz ID of the recording.

	Returns:
		requests.Response: The API response.
	"""

	request_headers: dict[str, str] = {
		"Authorization": f"Token {token}"
	}
	
	request_payload: dict[str, Any] = {
		"recording_mbid": musicbrainz_id,
		"score": 1
	}

	try:
		return (requests.post(
			listenbrainz_feedback_url,
			headers=request_headers,
			json=request_payload,
		))
	except Exception as exception:
		print(f"An exception was raised while attempting to send a request (to submit feedback): {exception}")
		sys.exit(1)


def submit_like_wrapper(
	listenbrainz_feedback_url: str,
	token: str,
	formatted_favourites: list[queries.Favourite],
	max_submit_attempts: int,
	seconds_before_reattempt: int
) -> None:
	"""
	Acts as a wrapper for the 'submit_like' function.

	Args:
		listenbrainz_feedback_url (str): The ListenBrainz feedback endpoint.
		token (str): The ListenBrainz user token.
		formatted_favourites (list[queries.Favourite]): All formatted favourites to submit.
		max_submit_attempts (int): Maximum number of submission attempts per favourite.
		seconds_before_reattempt (int): Seconds to wait before retrying a failed favourite.
	"""

	length_formatted_favourites: int = len(formatted_favourites)
	print(f"Submitting {length_formatted_favourites} favourites (feedbacks)...")

	for (count, favourite_row) in enumerate(formatted_favourites, start=1):
		for attempt in range(0, max_submit_attempts, 1):
			api_response: requests.Response = submit_like(listenbrainz_feedback_url, token, favourite_row.musicbrainz_id)
			print(f"{count}. {favourite_row.artist} - \"{favourite_row.title}\"'s status code: {api_response.status_code} ({attempt+1}° attempt)")

			if (api_response.ok):  #Code <400
				wait_for_rate_limit(api_response)
				break
			elif (attempt == (max_submit_attempts - 1)):
				print(f"\" {favourite_row.artist} - '{favourite_row.title}' \" aborted as {max_submit_attempts} attempts were reached.")
				break

			time.sleep(seconds_before_reattempt)

	return (None)
