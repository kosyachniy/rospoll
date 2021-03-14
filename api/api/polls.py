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
			'completed': [],
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

		if 'cover' in poll['questions'][i] and 'file' in poll['questions'][i]:
			try:
				file_type = poll['questions'][i]['file'].split('.')[-1]
			except:
				continue

			try:
				link = load_image(poll['questions'][i]['cover'], file_type)
				poll['questions'][i]['cover'] = link
			except:
				continue

	## Cover

	poll['cover'] = '0.png'

	if 'cover' in x:
		try:
			file_type = x['file'].split('.')[-1]

		# Invalid file extension
		except:
			raise ErrorInvalid('file')

		try:
			link = load_image(x['cover'], file_type)
			poll['cover'] = link

		# Error loading cover
		except:
			raise ErrorUpload('cover')

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
	else:
		db_filter['audience'] = True

		if this.user['admin'] >= 3:
			db_condition['completed'] = {'$ne': this.user['id']}

	polls = list(db['polls'].find(db_condition, db_filter).sort('created', -1))

	# Filter

	if this.user['admin'] >= 3 and not process_single:
		poll_id = 0

		while poll_id < len(polls):
			excluded = False

			for condition in polls[poll_id]['audience']:
				if 'answer' not in condition:
					continue

				excluded = True

				for answer in this.user['answers']:
					if condition['poll'] == answer['poll'] and condition['question'] == answer['question'] and condition['answer'] == answer['answer']:
						excluded = False
						break

				if not excluded: # хотя бы одно условие
					break

			if excluded:
				del polls[poll_id]
				continue

			poll_id += 1

	# Limits

	offset = x['offset'] if 'offset' in x else 0
	last = offset+x['count'] if 'count' in x else None

	polls = polls[offset:last]

	# Processing

	for i in range(len(polls)):
		## Cover
		polls[i]['cover'] = IMAGE['link_opt'] + polls[i]['cover']

		## Type
		polls[i]['type'] = 'reusable'

	# # Disposable

	# for i in range(len(polls)) // 2: # TODO: 3
	# 	pass

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
		('file', False, str),
	))

	# Access

	if this.user['admin'] < 3:
		raise ErrorAccess('token')

	# Process

	x['time'] = this.timestamp

	if 'file' in x:
		try:
			file_type = x['file'].split('.')[-1]

		# Invalid file extension
		except:
			raise ErrorInvalid('file')

		try:
			x['answer'] = load_image(x['answer'], file_type)

		# Error loading cover
		except:
			raise ErrorUpload('image')

		del x['file']

	# Save

	db['users'].update_one({'id': this.user['id']}, {'$push': {'answers': x}})

	# Cache: completed

	poll = db['polls'].find_one({'id': x['poll']}, {'_id': False, 'questions.id': True, 'completed': True, 'award': True})
	if poll:
		questions = set([i['id'] for i in poll['questions']])
		questions -= {x['question']}

		for question in this.user['answers']:
			if question['poll'] == x['poll']:
				questions -= {question['question']}

		if not len(questions) and this.user['id'] not in poll['completed']:
			db['polls'].update_one({'id': x['poll']}, {'$push': {'completed': this.user['id']}})
			db['users'].update_one({'id': this.user['id']}, {'$inc': {'balance': poll['award']}})

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

# Stats

def stat(this, **x):
	# Checking parameters

	check_params(x, (
		('poll', True, int),
	))

	# Get

	db_filter = {
		'_id': False,
		'questions.id': True,
		'questions.title': True,
		'questions.type': True,
		'questions.answers': True,
	}

	poll = db['polls'].find_one({'id': x['poll']}, db_filter)

	# Formating & Calculating

	for question_id in range(len(poll['questions'])):
		if 'answers' in poll['questions'][question_id]:
			for answer_id in range(len(poll['questions'][question_id]['answers'])):
				users = list(db['users'].find({'answers': {'$elemMatch': {
					'poll': x['poll'],
					'question': poll['questions'][question_id]['id'],
					'answer': poll['questions'][question_id]['answers'][answer_id]['id'],
					'blocked': {'$exists': False},
				}}}, {
					'_id': False,
					'vk': True,
				}))

				poll['questions'][question_id]['answers'][answer_id]['count'] = len(users)
				poll['questions'][question_id]['answers'][answer_id]['users'] = [user['vk'] for user in users]

			poll['questions'][question_id]['sum'] = sum([i['count'] for i in poll['questions'][question_id]['answers']])

			for answer_id in range(len(poll['questions'][question_id]['answers'])):
				if poll['questions'][question_id]['sum']:
					poll['questions'][question_id]['answers'][answer_id]['perc'] = round(poll['questions'][question_id]['answers'][answer_id]['count']*100/poll['questions'][question_id]['sum'], 1)
				else:
					poll['questions'][question_id]['answers'][answer_id]['perc'] = 0.
					poll['questions'][question_id]['answers'][answer_id]['users'] = []

		else:
			answers = {}

			users = list(db['users'].find({'answers': {'$elemMatch': {
				'poll': x['poll'],
				'question': poll['questions'][question_id]['id'],
				'blocked': {'$exists': False},
			}}}, {'_id': False, 'vk': True, 'answers': {'$elemMatch': {
				'poll': x['poll'],
				'question': poll['questions'][question_id]['id'],
			}}}))

			if users:
				for user in users:
					if user['answers'][-1]['answer'] in answers:
						answers[user['answers'][-1]['answer']].append(user['vk'])
					else:
						answers[user['answers'][-1]['answer']] = [user['vk']]

			answers_len = len(users)
			answers = [{
				'answer': answer,
				'users': answers[answer],
				'count': len(answers[answer]),
				'perc': round(len(answers[answer])*100/answers_len, 1),
			} for answer in answers]

			poll['questions'][question_id]['answers'] = answers
			poll['questions'][question_id]['sum'] = answers_len

	# Response

	return poll