import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
import requests
import logging
import json
import sys

from opcodes import *

INTENTS = 14023 #https://ziad87.net/intents/
TOKEN = None

getGateway = requests.get(
	url="https://discord.com/api/gateway/bot", 
	headers={"Authorization": f"Bot {TOKEN}"}
)
if getGateway.status_code == 401:
	logging.error("Missing token")
	sys.exit()

GATEWAY = getGateway.json()["url"]
DEBUG = True

async def heartbeat(websocket, **kwargs):
	if kwargs.get("interval") != None:
		while True:
			if DEBUG == True:
				logging.info('--- Heartbeat ---')
			await websocket.send(json.dumps({"op": opcodes.HEARTBEAT, "d": ResumeConnection.LATEST_SEQ}))
			await asyncio.sleep(kwargs.get("interval") / 1000)
	else:
		await websocket.send(json.dumps({"op": opcodes.HEARTBEAT, "d": ResumeConnection.LATEST_SEQ}))

async def identify(websocket):
	identify = {
		"op": opcodes.IDENTIFY, 
		"d": {
			"token": TOKEN, 
			"intents": INTENTS, 
			"properties": {
				"os": "linux", 
				"browser": "PK-4 Worker", 
				"device": "PK-4 Worker", 
				}
			}
		}
	logging.info("Sending 'identify' to gateway..")
	await websocket.send(json.dumps(identify))

class ResumeConnection:
	LATEST_SEQ = "null"
	SESSION_ID = None
	GATEWAY_ID = None

	def __init__(self, websocket):
		self.websocket = websocket

	def reconnect(self):
		logging.info("Resuming session..")
		resume = {
			"op": 6,
			"d": {
			    "token": TOKEN,
			  	"session_id": SESSION,
			  	"seq": LATEST_SEQ
			}
		}
		self.websocket.send(json.dumps(resume))

class messageHandler:
	def __init__(self, websocket, message):
		self.message = message
		self.handle = self.handler(self.message)

	def handler(self, message):
		if message["t"] == "READY":
			logging.info("Received 'READY' from gateway, handshake completed")
			ResumeConnection.SESSION_ID = message["d"]["session_id"]
			ResumeConnection.GATEWAY_ID = message["d"]["resume_gateway_url"]
		print(message)

async def main():
	async with connect(GATEWAY) as websocket:
		async for websocket in connect(GATEWAY):
			try:
				ack = await websocket.recv()
				ack = json.loads(ack)
				logging.info("Received 'Hello' from gateway, starting heartbeat-cycle..")
				asyncio.create_task(
					heartbeat(
						websocket, interval=ack["d"]["heartbeat_interval"]
						)
					)
				await identify(websocket)
				async for message in websocket:
					message = json.loads(message)
					if message["op"] == opcodes.DISPATCH:
						ResumeConnection.LATEST_SEQ = message["s"]
						messageHandler(websocket, message)
					if DEBUG == True:
						if message["op"] == opcodes.HEARTBEAT:
							logging.info(f"Recieved op: {message['op']}, sending heartbeat ASAP..")
							await heartbeat(websocket)
						if message["op"] == opcodes.HEARTBEAT_ACK:
							logging.info(f"Recieved op: {message['op']}, Heartbeat acknowledged..")
					elif message["op"] == opcodes.RECONNECT:
						logging.warning("Received 'RECONNECT', attempting to resume..")
						logging.warning(message)
					elif message["op"] == opcodes.INVALID_SESSION and message["d"] == False:
						logging.warning(f"INVALID_SESSION, {message}")

			except ConnectionClosed as cc: # recv(), send(), and similar methods raise the exception when the connection is closed.
				try:
					ResumeConnection(websocket).reconnect()
				except:
					logging.error("ConnectionClosed:" + cc)
			except ConnectionClosedOK as cco:
				try:
					ResumeConnection(websocket).reconnect()
				except:
					logging.error("ConnectionClosedOK" + cco)
			except ConnectionClosedError as cce:
				try:
					ResumeConnection(websocket).reconnect()
				except:
					logging.error("ConnectionClosedError" + cce)

if __name__=="__main__":
	logging.basicConfig(
		level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)
	asyncio.run(main())