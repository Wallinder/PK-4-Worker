import requests
import asyncio
import logging
import json

class Command:
	def __init__(self, msg, api, token):
		self.msg = msg
		self.api = api
		self.token = token
		self.headers = {
			"Authorization": f"Bot {token}",
			"Content-Type": "application/json"
		}
		self.guild = self.msg["d"]["guild_id"]
		self.channel_id = self.msg["d"]["channel_id"]
		self.user = self.msg["d"]["author"]["username"]
		self.command = self.msg["d"]["content"].split(" ")
		try:
			if self.command[1] == "get":
				print(self.msg)

			elif self.command[1] == "create":
				pass

			elif self.command[1] == "delete":
				pass

		except IndexError:
			send = requests.post(
				self.api + f"/channels/{self.channel_id}/messages", 
				headers=self.headers, 
				data=json.dumps(
						{
						  "content": "```placeholder```",
						  "tts": "false",
						}
					)
				).json()

	def _createVoiceChannel():
		pass


