import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from dotenv import load_dotenv
import requests
import logging
import json
import sys
import os
import signal
import aiohttp

from constants import *
from commands import *

INTENTS = 14023 #https://ziad87.net/intents/
DEBUG = False
API = "https://discord.com/api/v10"

load_dotenv()

TOKEN = os.getenv("TOKEN", None)

if TOKEN == None:
	logging.error("Unable to find token")
	sys.exit()

async def fetch_gateway():
    async with aiohttp.ClientSession() as session:
        async with session.get(API + "/gateway/bot", headers={"Authorization": f"Bot {TOKEN}"}) as response:
            if response.status == 401:
                logging.error("Invalid or missing token.")
                sys.exit(1)
            return (await response.json())["url"]

GATEWAY = asyncio.run(fetch_gateway())


async def heartbeat(websocket, **kwargs) -> None:
	try:
		if kwargs.get("interval") != None:
			while True:
				if DEBUG == True:
					logging.info('--- Heartbeat ---')
				await websocket.send(json.dumps({"op": opcodes.HEARTBEAT, "d": ResumeConnection.LATEST_SEQ}))
				await asyncio.sleep(kwargs.get("interval") / 1000)
		else:
			await websocket.send(json.dumps({"op": opcodes.HEARTBEAT, "d": ResumeConnection.LATEST_SEQ}))
	except ConnectionClosedOK as cco:
		try:
			ResumeConnection(websocket).reconnect()
		except:
			logging.error("ConnectionClosedOK:" + cco)

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
	logging.info("Sending 'IDENTIFY' to gateway..")
	await websocket.send(json.dumps(identify))

class ResumeConnection:
	LATEST_SEQ = "null"
	SESSION_ID = None
	GATEWAY_ID = None

	def __init__(self, websocket):
		self.websocket = websocket

async def reconnect(self):
    logging.info("Resuming session...")
    resume = {
        "op": opcodes.RESUME,
        "d": {
            "token": TOKEN,
            "session_id": ResumeConnection.SESSION_ID,
            "seq": ResumeConnection.LATEST_SEQ
        }
    }
    await self.websocket.send(json.dumps(resume))


class messageHandler:
	def __init__(self, websocket, msg):
		self.msg = msg
		self.ready = self.ready()
		self.command = self.filterCommands()

	def ready(self):
		if self.msg["t"] == "READY":
			logging.info("Received 'READY' from gateway, handshake completed")
			ResumeConnection.SESSION_ID = self.msg["d"]["session_id"]
			ResumeConnection.GATEWAY_ID = self.msg["d"]["resume_gateway_url"]
			#for guild in msg["d"]["guilds"]:
			#	print(guild["id"])
	def filterCommands(self):
		if self.msg["t"] == "MESSAGE_CREATE" and self.msg["d"]["content"].split(" ")[0] == "pk4ctl":
			Command(self.msg, API, TOKEN)

async def main():
	async with connect(GATEWAY) as websocket:
		async with connect(GATEWAY) as websocket:
				try:
        			ack = await websocket.recv()
        			ack = json.loads(ack)
        			logging.info("Received 'HELLO' from gateway, starting heartbeat-cycle..")
        			asyncio.create_task(heartbeat(websocket, interval=ack["d"]["heartbeat_interval"]))
        			await identify(websocket)
        			async for message in websocket:
            			# Process messages
    				except ConnectionClosed as cc:
        			# Handle connection errors

			except ConnectionClosed as cc: # recv(), send(), and similar methods raise the exception when the connection is closed.
    				logging.error(f"Connection closed unexpectedly: {cc}")
			
			except ConnectionClosedOK as cco:
				try:
					ResumeConnection(websocket).reconnect()
				except:
					logging.error("ConnectionClosedOK" + cco)
					
			except Exception as e:
				logging.error(f"Unexpected error: {e}")

if __name__=="__main__":
	logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
		level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)
	asyncio.run(main())

def shutdown():
    logging.info("Shutting down bot...")
    sys.exit(0)

signal.signal(signal.SIGINT, lambda *_: shutdown())
