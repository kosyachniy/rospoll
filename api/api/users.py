from api._func.mongodb import db
from api._func.vk_app import notify as notify_vk
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
		'blocked': True,
		'last': True,
		'answers': True,
	}

	#

	users = list(db['users'].find(db_condition, db_filter))
	users = sorted(users, key=lambda i: i['time'])[::-1]

	# Count

	count = x['count'] if 'count' in x else None
	users = users[:count]

	# Processing

	for i in range(len(users)):
		users[i]['polls'] = len(set({j['poll'] for j in users[i]['answers']}))
		del users[i]['answers']

	# Response

	res = {
		'users': users,
	}

	return res

def block(this, **x):
	# Checking parameters

	check_params(x, (
		('id', True, int),
	))

	# Update

	user = db['users'].find_one({'id': x['id']}, {'_id': False, 'blocked': True})

	if user is None:
		raise ErrorWrong('id')

	if 'blocked' not in user:
		db['users'].update_one({'id': x['id']}, {'$set': {'blocked': True}})
	else:
		db['users'].update_one({'id': x['id']}, {'$unset': {'blocked': ''}})

def notify(this, **x):
	# Checking parameters

	check_params(x, (
		('id', False, int),
		('text', True, str),
	))

	#

	if 'id' not in x:
		x['id'] = 0

	#

	if x['id']:
		poll = db['polls'].find_one({'id': x['id']}, {'_id': False, 'audience': True})

		if len(poll['audience']):
			cond = {}

			for field in ('poll', 'question', 'answer'):
				if field in poll['audience'][0]:
					cond[field] = poll['audience'][0][field]

			users = [user['vk'] for user in db['users'].find({
				'answers': {'$elemMatch': cond},
			}, {
				'_id': False,
				'vk': True,
			})]

		else:
			users = [user['vk'] for user in db['users'].find({}, {'_id': False, 'vk': True})]

	else:
		users = [user['vk'] for user in db['users'].find({}, {'_id': False, 'vk': True})]

	print('NOTIFY', x['id'], users)

	notify_vk(users, x['text'])