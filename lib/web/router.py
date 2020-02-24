import json
from lib.web import app

@app.route('/')
def index():
	return "Running", 200
