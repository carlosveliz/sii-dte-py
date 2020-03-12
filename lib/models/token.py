import datetime

class Token():
	_token_string = ''
	_expiry_date = None

	def __init__(self, token_string):
		_token_string = token_string
		""" Expire after 10 min """
		_expiry_date = datetime.now().min + 10

	def __str__(self):
		return _token_string

	def get_token(sef):
		if not _is_expired:
			return _token_string
		else:
			raise TokenExpiredError()

	def _is_expired(self):
		return datetime.now() >= _expiry_date

class TokenExpiredError(Exception):
	""" Raised on token expiration """
