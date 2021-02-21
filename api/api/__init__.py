import time

from api._func.mongodb import db
from api._func import get_language
import api._error as Error

import api.account as account
import api.users as users
import api.polls as polls
# TODO: from api import *


class API():
	def __init__(self, server, client, sio=None):
		self.server = server
		self.client = client
		self.sio = sio

		# Reset online users
		db['online'].remove()

	def method(self, name, params={}, ip=None, ip_remote=None, jwt={}): # TODO: network
		self.timestamp = time.time()
		self.ip = ip

		# User recognition

		self.user = {
			'id': 0,
			'admin': 2,
		}

		if jwt:
			user = db['users'].find_one({'vk': jwt['user_id']})
			user['admin'] = 3

			if user:
				self.user = user

		# IP (case when a web application makes requests from IP with the same address)

		if ip_remote and ip == self.client['ip']:
			self.ip = ip_remote

		# Remove extra indentation

		for i in params:
			if type(params[i]) == str:
				params[i] = params[i].strip()

		# # Action tracking

		# req = {
		# 	'time': self.timestamp,
		# 	'user': self.user['id'],
		# 	'ip': self.ip,
		# 	'method': name,
		# 	'params': params,
		# }

		# db['actions'].insert_one(req)

		# API method

		try:
			module, method = name.split('.')
			func = getattr(globals()[module], method)
		except:
			raise Error.ErrorWrong('method')

		# Request

		return func(self, **params)