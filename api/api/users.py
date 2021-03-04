from api._func.mongodb import db
from api._error import ErrorWrong, ErrorAccess, ErrorBlock
from api._func import check_params


def get(this, **x):
	# Checking parameters

	check_params(x, (
		('id', False, (int, list), int),
		('count', False, int),
		('fields', False, list, str),
	))

	# Condition formation

	process_one = False

	if 'id' in x:
		if type(x['id']) == int:
			db_condition = {
				'id': x['id'],
			}

			process_one = True

		else:
			db_condition = {
				'id': {'$in': x['id']},
			}

	else:
		db_condition = {
			'login': {'$ne': 'admin'},
		}

	# Get users

	db_filter = {
		'_id': False,
		'id': True,
		'vk': True,
		'time': True,
		'name': True,
		'surname': True,
		'balance': True,
		'sex': True,
		'city': True,
		'country': True,
		'bdate': True,
		'photo': True,
		'timezone': True,
		'phone': True,
		'mail': True,
	}

	#

	users = list(db['users'].find(db_condition, db_filter))
	users = sorted(users, key=lambda i: i['time'])[::-1]

	# Count

	count = x['count'] if 'count' in x else None
	users = users[:count]

	# Response

	res = {
		'users': users,
	}

	return res

# # Block

# def block(this, **x):
# 	# Checking parameters

# 	check_params(x, (
# 		('id', True, int),
# 	))

# 	# Get user

# 	users = db['users'].find_one({'id': x['id']})

# 	## Wrond ID
# 	if not users:
# 		raise ErrorWrong('id')

# 	# No access
# 	if this.user['admin'] < 6 or users['admin'] > this.user['admin']:
# 		raise ErrorAccess('block')

# 	# Change status
# 	users['admin'] = 1

# 	# Save
# 	db['users'].save(users)