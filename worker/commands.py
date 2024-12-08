import requests
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
		self.command = self.msg["d"]["content"].lower().split(" ")
		try:
			if self.command[1] == "get":
				if self.command[2] == "arnebergli":
					if self.command[3] == "ansattliste":
						self.sendMessage(arnebergli().ansatt()[0])
					elif self.command[3] == "ansatt":
						self.sendMessage(arnebergli().ansatt()[1][self.command[4]])
						
			elif self.command[1] == "create":
				pass

			elif self.command[1] == "delete":
				pass

		except IndexError:
			self.sendMessage("```placeholder```")

	def sendMessage(self, content):
		send = requests.post(
			self.api + f"/channels/{self.channel_id}/messages", 
			headers=self.headers, 
			data=json.dumps(
					{
					"content": f"{content}",
					"tts": "false",
					}
				)
			).json()
			

