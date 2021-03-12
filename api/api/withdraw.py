from api._error import ErrorAccess
from api._func import check_params, next_id
from api._func.mongodb import db


def add(this, **x):
	# Checking parameters
	check_params(x, (
		('type', True, int),
		('details', True, str),
	))

	# No access
	if this.user['admin'] < 3:
		raise ErrorAccess('withdraw')

	#

	withdraw = {
		'id': next_id('withdraw'),
		'user': this.user['id'],
		'time': this.timestamp,
		'type': x['type'],
		'details': x['details'],
	}

	db['withdraw'].insert_one(withdraw)

def get(this, **x):
	return list(db['withdraw'].find({}, {'_id': False}))