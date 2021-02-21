# Params
from sets import SERVER, CLIENT

# Main app

from flask import Flask
app = Flask(__name__)

# CORS

from flask_cors import CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# Limiter

from flask import request, jsonify
from flask_limiter import Limiter

def get_unique_code():
	header = request.headers.get('Authorization')

	try:
		token = header.split(' ')[1]
	except:
		pass
	else:
		if token:
			return token
	try:
		url = request.json['url']
	except:
		pass
	else:
		if url:
			return url

	return request.remote_addr

limiter = Limiter(
	app,
	key_func=get_unique_code,
	default_limits=['1000/day', '500/hour', '20/minute'] # TODO: fix
)

# API
## Libraries
import json
from functools import wraps

import jwt

from api import API, Error

## Global variables
api = API(
	server=SERVER,
	client=CLIENT,
)


with open('keys.json', 'r') as file:
	SECRET_KEY = json.loads(file.read())['jwt']

## JWT
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		try:
			header = request.headers.get('Authorization')
			token = header.split(' ')[1]

			if not token:
				return jsonify({'message': 'Token is missing!'}), 403

			try:
				data = jwt.decode(token, SECRET_KEY)
				kwargs['data'] = data
			except:
				return jsonify({'message': 'Token is invalid!'}), 403

			return f(*args, **kwargs)

		except Exception as e:
			print('ERR', e)
			return f(*args, **kwargs)

	return decorated

## Endpoints
@app.route('/', methods=['POST'])
@token_required
def index(data={}):
	x = request.json
	# print(x, data)

	# All required fields are not specified
	for field in ('method',):
		if field not in x:
			return jsonify({'error': 2, 'result': 'All required fields are not specified!'})

	# Call API

	req = {}

	try:
		res = api.method(
			x['method'],
			x['params'] if 'params' in x else {},
			ip=request.remote_addr,
			ip_remote=x['ip'] if 'ip' in x else None,
			jwt=data,
		)

	except Error.BaseError as e:
		req['error'] = e.code
		req['result'] = str(e)

	# except Exception as e:
	# 	req['error'] = 1
	# 	req['result'] = 'Server error'

	else:
		req['error'] = 0

		if res:
			req['result'] = res

	return jsonify(req)