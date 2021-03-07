import datetime
import re
import hashlib
import json
import jwt
from base64 import b64encode
from collections import OrderedDict
from hmac import HMAC
from urllib.parse import urlparse, parse_qsl, urlencode

from sets import CLIENT, IMAGE
from api._error import ErrorWrong, ErrorInvalid, ErrorAccess
from api._func import check_params, next_id
from api._func.mongodb import db


with open('keys.json', 'r') as file:
	keys = json.loads(file.read())
	CLIENT_SECRET = keys['vk']['client_secret']
	SECRET_KEY = keys['jwt']


# Account registration

def registrate(vk, timestamp):
	# ID

	user_id = next_id('users')

	#

	req = {
		'id': user_id,
		'vk': vk,
		'time': timestamp,
		'last': timestamp,
		'balance': 0.,
		'name': '',
		'answers': [],
	}

	# Save

	db['users'].insert_one(req)

	# Response

	del req['_id']
	return req

def is_valid_vk(*, query: dict) -> bool:
	vk_subset = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
	hash_code = b64encode(HMAC(CLIENT_SECRET.encode(), urlencode(vk_subset, doseq=True).encode(), hashlib.sha256).digest())
	decoded_hash_code = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
	return query["sign"] == decoded_hash_code

# Sign in / Sign up

def auth(this, **x):
	# Checking parameters

	check_params(x, (
		('url', False, str),
		('login', False, str),
		('password', False, str),
	))

	# Admin

	if 'login' in x:
		db_condition = {
			'login': x['login'],
			'password': hashlib.md5(bytes(x['password'], 'utf-8')).hexdigest(),
		}

		user = db['users'].find_one(db_condition, {'_id': False, 'id': True})

		if user:
			token = jwt.encode({
				'user_id': 0,
				'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
			}, SECRET_KEY).decode('UTF-8')

			return token

		raise ErrorAccess('admin')

	# VK auth

	try:
		params = dict(parse_qsl(urlparse(x['url']).query, keep_blank_values=True))
		social_id = int(params['vk_user_id'])
		status = is_valid_vk(query=params)
	except:
		raise ErrorInvalid('url')

	if not status:
		raise ErrorWrong('url')

	# JWT

	token = jwt.encode({
		'user_id': social_id,
		'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
	}, SECRET_KEY).decode('UTF-8')

	#

	new = False
	user = db['users'].find_one({'vk': social_id}, {'_id': True})

	if not user:
		registrate(
			social_id,
			this.timestamp,
		)

		new = True

	else:
		db['users'].update_one({'vk': social_id}, {'$set': {'last': this.timestamp}})

	#

	db_filter = {
		'_id': False,
		'balance': True,
	}

	res = db['users'].find_one({'vk': social_id}, db_filter)

	# Response

	res['new'] = new
	res['token'] = token

	return res

# Edit

def edit(this, **x):
	# Checking parameters
	check_params(x, (
		('name', False, str),
		('surname', False, str),
		('sex', False, int),
		('city', False, dict),
		('country', False, dict),
		('bdate', False, str),
		('photo', False, str),
		('timezone', False, int),
		('phone', False, str),
		('mail', False, str),
	))

	# No access
	if this.user['admin'] < 3:
		raise ErrorAccess('edit')

	# Change fields
	for i in ('name', 'surname', 'sex', 'city', 'country', 'bdate', 'photo', 'timezone', 'phone', 'mail'):
		if i in x:
			this.user[i] = x[i]

	# Save changes
	db['users'].save(this.user)

	# Response
	del this.user['_id']
	del this.user['vk']
	return this.user