from api._error import ErrorAccess, ErrorEmpty # , ErrorBlock
from api._func import check_params, next_id
from api._func.mongodb import db


def add(this, **x):
	# Checking parameters
	check_params(x, (
		('type', True, int),
		('details', True, str),
	))

	# Errors
	## No access
	if this.user['admin'] < 3:
		raise ErrorAccess('withdraw')

	## No balance
	if not this.user['balance']:
		raise ErrorEmpty('balance')

	# ## Blocked
	# if 'blocked' in this.user:
	# 	raise ErrorBlock('user')

	#

	withdraw = {
		'id': next_id('withdraw'),
		'user': this.user['id'],
		'time': this.timestamp,
		'type': x['type'],
		'details': x['details'],
		'status': 1,
		'count': this.user['balance'],
	}

	db['withdraw'].insert_one(withdraw)

	#

	db['users'].update_one({'id': this.user['id']}, {'$set': {'balance': 0}})

def get(this, **x):
	# No access
	if this.user['admin'] < 3:
		raise ErrorAccess('get')

	return list(db['withdraw'].find({'status': 1}, {'_id': False, 'status': False}))

def close(this, **x):
	# Checking parameters
	check_params(x, (
		('id', True, int),
	))

	# No access
	if this.user['admin'] < 3:
		raise ErrorAccess('close')

	#

	db['withdraw'].update_one({'id':x['id']}, {'$set': {'status': 0}})