import subprocess, platform
from datetime import datetime
from typing import Any


# Pretty long type aliases because I love to statically type in Python. <3
ScrobbleRow = tuple[int|None, str, str, str, str|None]
FavouriteRow = tuple[str, str, str|None]


def clear_screen() -> None:
	"""Unsurprisingly, should clear the terminal screen; working on both POSIX and Windows!!1!"""

	command: str = ("clear" if (platform.system() != "Windows") else "cls")
	subprocess.run(command, shell=True)

	return (None)


def ask_yes_no(question: str) -> bool:
	"""
	Asks the user a simple yes or no question.

	Args:
		question (str): The question to display to the user.

	Returns:
		bool: 'True' if the user answered with "y" or "yes", 'False' otherwise.
	"""

	answer: str = input(question + " (y/N): ").strip().lower()
	return (answer in ["y", "yes"])


def validate_date(date_string: str) -> bool:
	"""
	Validates whether a string matches the YYYY-MM-DD (ISO 8601 for dates) date format.

	Args:
		date_string (str): The date string to validate.

	Returns:
		bool: 'True' if the date is valid, 'False' otherwise.
	"""
	
	try:
		datetime.strptime(date_string, "%Y-%m-%d")
		return (True)
		
	except ValueError:
		return (False)


def namedtuple_to_dict(obj: Any) -> Any:
	"""Converts NamedTuple instances to dictionaries and strips out None values.

	Args:
		obj (Any): The object to convert.

	Returns:
		Any: When given a 'NamedTuple' a 'dict' will be returned, otherwise will return 'obj' as-is.
	"""

	# if hasattr(obj, "_asdict"):	#Check if the object is a 'NamedTuple' because, unlike normal
	# 								#tuples, it contains the method "_asdict".
	# 	result_dictionary: dict[str, Any] = {}

	# 	for (key, value) in obj._asdict().items():
	# 		if (value != None):		#In this case, 'additional_info' can be 'None'. If so, it is simply not added in the dict.
	# 			result_dictionary[key] = namedtuple_to_dict(value)

	# 	return (result_dictionary)

	# return (obj) 					#Return a non-'NamedTuple' as-is. It is mainly for the recursion.

	if hasattr(obj, '_asdict'):
		return {
			key: namedtuple_to_dict(value) for (key, value) in obj._asdict().items() if (value != None)
		}

	return (obj)
