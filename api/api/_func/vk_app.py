import json

import vk


with open('keys.json', 'r') as file:
	VK_API_ACCESS_TOKEN = json.loads(file.read())['vk']['token']

from sets import VK_API_VERSION


session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)


def notify(users, text):
	return api.notifications.sendMessage(user_ids=users, message=text)