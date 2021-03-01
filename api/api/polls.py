import time
import re
# import shutil

from sets import IMAGE
from api._func.mongodb import db
from api._error import ErrorInvalid, ErrorAccess, ErrorWrong, ErrorUpload
from api._func import reimg, get_user, check_params, next_id, load_image


# Add / edit

def add(this, **x):
	# Checking parameters

	# Edit
	if 'id' in x:
		check_params(x, (
			('id', True, int),
			('title', False, str),
			('description', False, str),
			('outro', False, str),
			('audience', False, list, dict),
			('cover', False, str),
			('file', False, str),
			('questions', False, list, dict),
			('award', False, (float, int)),
			('time', False, int),
			('section', False, str),
		))

	# Add
	else:
		check_params(x, (
			('title', True, str),
			('description', True, str),
			('outro', True, str),
			('audience', True, list, dict),
			('cover', True, str),
			('file', True, str),
			('questions', True, list, dict),
			('award', True, (float, int)),
			('time', True, int),
			('section', True, str),
		))

	if 'cover' in x and not x['cover']:
		raise ErrorInvalid('cover')

	if 'file' in x and not x['file']:
		raise ErrorInvalid('file')

	# Process of poll

	processed = False

	# poll formation

	if 'id' in x:
		poll = db['polls'].find_one({'id': x['id']})

		# Wrong ID
		if not poll:
			raise ErrorWrong('id')

	else:
		poll = {
			'id': next_id('polls'),
			'created': this.timestamp,
		}

	# Change fields

	for field in ('title', 'description', 'audience', 'questions', 'award', 'time', 'section', 'outro'):
		if field in x:
			poll[field] = x[field]

	question_id = 0
	for i in range(len(poll['questions'])):
		question_id += 1
		poll['questions'][i]['id'] = question_id + 0

		if 'answers' in poll['questions'][i]:
			answer_id = 0
			for j in range(len(poll['questions'][i]['answers'])):
				answer_id += 1
				poll['questions'][i]['answers'][j] = {
					'id': answer_id + 0,
					'answer': poll['questions'][i]['answers'][j],
				}

	## Cover

	poll['cover'] = '0.png'

	if 'cover' in x:
		try:
			file_type = x['file'].split('.')[-1]

		# Invalid file extension
		except:
			raise ErrorInvalid('file')

		# try:
		link = load_image(x['cover'], file_type)
		poll['cover'] = link

		# # Error loading cover
		# except:
		# 	raise ErrorUpload('cover')

	# Save poll
	db['polls'].save(poll)

	# Response

	res = {
		'id': poll['id'],
	}

	if processed:
		res['cont'] = poll['cont']

	return res

# Get

def get(this, **x):
	# Checking parameters

	check_params(x, (
		('id', False, (int, list), int),
		('count', False, int),
		('offset', False, int),
	))

	# Condition formation

	process_single = False

	db_condition = {}

	if 'id' in x:
		if type(x['id']) == int:
			db_condition['id'] = x['id']

			process_single = True

		else:
			db_condition['id'] = {'$in': x['id']}

	# Get

	count = x['count'] if 'count' in x else None

	db_filter = {
		'_id': False,
		'id': True,
		'title': True,
		'description': True,
		'time': True,
		'cover': True,
		'award': True,
	}

	if process_single:
		db_filter['questions'] = True
		db_filter['outro'] = True

	polls = list(db['polls'].find(db_condition, db_filter).sort('created', -1))

	offset = x['offset'] if 'offset' in x else 0
	last = offset+x['count'] if 'count' in x else None

	polls = polls[offset:last]

	# Processing

	for i in range(len(polls)):
		## Cover
		polls[i]['cover'] = IMAGE['link_opt'] + polls[i]['cover']

		## Type
		polls[i]['type'] = 'reusable'

	# Response

	res = {
		'polls': polls,
	}

	return res

# Answer

def answer(this, **x):
	# Checking parameters

	check_params(x, (
		('poll', True, int),
		('question', True, int),
		('answer', True, (list, int, str)),
	))

	#

	if this.user['admin'] < 3:
		raise ErrorAccess('token')

	db['users'].update_one({'id': this.user['id']}, {'$push': {'answers': x}})

# Delete

def delete(this, **x):
	# Checking parameters

	check_params(x, (
		('id', True, int),
	))

	# Get

	poll = db['polls'].find_one({'id': x['id']})

	## Wrong ID
	if not poll:
		raise ErrorWrong('id')

	# Delete

	db['polls'].remove(poll)

# Get all

def audience(this, **x):
	# Checking parameters

	check_params(x, (
		('poll', False, int),
		('question', False, int),
	))

	# Polls

	if 'poll' not in x:
		return list(db['polls'].find({}, {'_id': False, 'id': True, 'title': True}))

	# Questions

	db_condition = {
		'id': x['poll'],
	}

	if 'question' not in x:
		poll = db['polls'].find_one(db_condition, {'_id': False, 'questions.id': True, 'questions.title': True})

		try:
			return poll['questions']
		except:
			return []

	# Answers

	db_condition['questions.id'] = x['question']

	poll = db['polls'].find_one(db_condition, {'_id': False, 'questions.answers': True})

	try:
		return poll['questions'][0]['answers']
	except:
		return []