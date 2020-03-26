import datetime

class Token():
	_token_string = ''
	_expiry_date = None

	def __init__(self, token_string):
		self._token_string = token_string
		""" Expire after 10 min """
		self._expiry_date = datetime.datetime.now() + datetime.timedelta(0,60*10)

	def __str__(self):
		return _token_string

	def get_token(self):
		if not self._is_expired():
			return self._token_string
		else:
			raise TokenExpiredError()

	def _is_expired(self):
		return datetime.datetime.now() >= self._expiry_date

	def to_json(self):
		return '{"token":"' + self._token_string + '", "expiry":"' + str(self._expiry_date) + '"}'

class TokenExpiredError(Exception):
	""" Raised on token expiration """
