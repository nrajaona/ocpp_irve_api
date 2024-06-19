import asyncio
import websockets
from fastapi import WebSocket
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from dotenv import load_dotenv
import os
import logging

load_dotenv()

WEBSOCKET_URL = os.getenv("WEBSOCKET_URL_LOCALHOST")
CHARGE_POINT_ID = os.getenv("CHARGE_POINT_ID")
CHARGE_POINT_MODEL = os.getenv("CHARGE_POINT_MODEL")
CHARGE_POINT_VENDOR = os.getenv("CHARGE_POINT_VENDOR")

logging.basicConfig(level=logging.INFO)

class ChargePoint(cp):
    async def send_boot_notification(self):
        try:
            request = call.BootNotificationPayload(
                charge_point_model=CHARGE_POINT_MODEL,
                charge_point_vendor=CHARGE_POINT_VENDOR
            )
            response = await self.call(request)
            if response.status == "Accepted":
                logging.info("Boot notification accepted")
            else:
                logging.error(f"Boot notification failed with status: {response.status}")
        except Exception as e:
            logging.error(f"Exception during boot notification: {e}")

    async def start_transaction(self):
        try:
            request = call.StartTransactionPayload(
                connector_id=1,
                id_tag="ABC123",
                meter_start=0,
                timestamp="2023-05-21T15:00:00Z"
            )
            response = await self.call(request)
            if response.id_tag_info["status"] == "Accepted":
                logging.info("Transaction started")
            else:
                logging.error(f"Start transaction failed with status: {response.id_tag_info['status']}")
        except Exception as e:
            logging.error(f"Exception during start transaction: {e}")

    async def stop_transaction(self):
        try:
            request = call.StopTransactionPayload(
                transaction_id=1,
                meter_stop=10,
                timestamp="2023-05-21T16:00:00Z"
            )
            response = await self.call(request)
            if response.id_tag_info["status"] == "Accepted":
                logging.info("Transaction stopped")
            else:
                logging.error(f"Stop transaction failed with status: {response.id_tag_info['status']}")
        except Exception as e:
            logging.error(f"Exception during stop transaction: {e}")

    async def status_notification(self):
        try:
            request = call.StatusNotificationPayload(
                connector_id=1,
                error_code="NoError",
                status="Available",
                timestamp="2023-05-21T15:00:00Z"
            )
            response = await self.call(request)
            return response
        except Exception as e:
            logging.error(f"Exception during status notification: {e}")
    
    async def send_command(self, command):
        if command == "start_charging":
            await self.start_transaction()
        elif command == "stop_charging":
            await self.stop_transaction()
        elif command == "status_notification":
            return await self.status_notification()
        
    async def send_heartbeat(self):
        try:
            request = call.HeartbeatPayload()
            response = await self.call(request)
            return response
        except Exception as e:
            logging.error(f"Exception during heartbeat: {e}")

    async def change_configuration(self, key: str, value: str):
        message = {
            "MessageTypeId": 2,  # CALL
            "UniqueId": "uniqueIdChangeConfiguration",
            "Action": "ChangeConfiguration",
            "Payload": {
                "key": key,
                "value": value
            }
        }
        return await self.send_command(json.dumps(message))
    

async def websocket_endpoint(websocket: WebSocket):
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            charge_point = ChargePoint(CHARGE_POINT_ID, ws)
            await charge_point.start()

            while True:
                data = await websocket.receive_text()
                logging.info(f"Message reçu: {data}")

                response = await charge_point.send_command(data)
                logging.info(f"Réponse envoyée: {response}")
                await websocket.send_text(f"Message reçu : {data}, Réponse : {response}")
    except websockets.ConnectionClosedOK:
        logging.info("Connection closed normally")
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket: {e}")