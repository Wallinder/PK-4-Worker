import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
import requests
import logging
import json
from opcodes import opcodes

token = "MTE2NjA4MDgzNjI5OTM5MTAyNg.GSgp1R.LMeVHWJJFRvGCDIxq3I6RfCUIsRvgklgvmK91Q"
gateway = requests.get(url="https://discord.com/api/gateway/bot", headers={"Authorization": f"Bot {token}"}).json()["url"]

async def heartbeat(websocket, **kwargs):
	if kwargs.get("interval") != None:
		while True:
			logging.info('--- Heartbeat ---')
			await websocket.send(json.dumps({"op": opcodes.HEARTBEAT, "d": "null"}))
			await asyncio.sleep(kwargs.get("interval") / 1000)
	else:
		logging.info('--- Heartbeat ---')
		await websocket.send(json.dumps({"op": opcodes.HEARTBEAT, "d": "null"}))

async def identify(websocket):
	identify = {
		"op": opcodes.IDENTIFY, 
		"d": {
			"token": token, 
			"intents": 513, 
			"properties": {
				"os": "linux", 
				"browser": "PK-4 WorkerDroid", 
				"device": "PK-4 WorkerDroid",
				}
			}
		}
	logging.info("Sending 'identify' to gateway..")
	await websocket.send(json.dumps(identify))

class ResumeConnection:
	LATEST_SEQ = None
	SESSION_ID = None
	GATEWAY_ID = None

	def __init__(self, websocket):
		self.websocket = websocket

	def reconnect(self):
		logging.info("Resuming session..")
		resume = {
			"op": 6,
			"d": {
			    "token": token,
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
	async with connect(gateway) as websocket:
		async for websocket in connect(gateway):
			try:
				ack = await websocket.recv()
				ack = json.loads(ack)
				logging.info("Received 'Hello' from gateway, sending heartbeat..")
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
					elif message["op"] == opcodes.HEARTBEAT:
						logging.info(f"Recieved op: {message['op']}, sending heartbeat ASAP..")
						await heartbeat(websocket)
					elif message["op"] == opcodes.HEARTBEAT_ACK:
						logging.info(f"Recieved op: {message['op']}, Heartbeat acknowledged..")
					elif message["op"] == opcodes.RECONNECT:
						logging.warning("Received 'RECONNECT', attempting to resume..")
						raise ConnectionClosed
					elif message["op"] == opcodes.INVALID_SESSION and message["d"] == True:
						logging.warning(f"INVALID_SESSION, {message}")
						raise ConnectionClosed
			except ConnectionClosed:
				ResumeConnection(websocket).reconnect()
				continue

if __name__=="__main__":
	logging.basicConfig(
		level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)
	asyncio.run(main())