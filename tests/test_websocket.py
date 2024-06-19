import asyncio
import websockets
import logging
import os
from dotenv import load_dotenv
import json

# Charger les variables d'environnement depuis .env
load_dotenv()

WEBSOCKET_URL = os.getenv("WEBSOCKET_URL_LOCALHOST")
OCPP_PROTOCOL = "ocpp1.6"  # Spécifiez le protocole OCPP ici

# Configurer le logging pour afficher les messages de niveau DEBUG
logging.basicConfig(level=logging.DEBUG)

async def test_websocket():
    try:
        logging.info(f"Attempting to connect to WebSocket URL: {WEBSOCKET_URL}")
        async with websockets.connect(WEBSOCKET_URL, subprotocols=[OCPP_PROTOCOL]) as ws:
            logging.info("Connexion WebSocket établie")

            # Test BootNotification
            boot_notification_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueId123",  # Unique ID for the message
                "BootNotification",  # Action
                {
                    "chargePointVendor": os.getenv("CHARGE_POINT_VENDOR"),
                    "chargePointModel": os.getenv("CHARGE_POINT_MODEL")
                }
            ])
            logging.debug(f"Envoi du message BootNotification: {boot_notification_message}")
            await ws.send(boot_notification_message)
            response = await ws.recv()
            logging.info(f"Réponse BootNotification reçue: {response}")

            # Test StatusNotification
            status_notification_message = json.dumps([
                2,
                "uniqueId456",
                "StatusNotification",
                {
                    "connectorId": 1,
                    "status": "Available"
                }
            ])
            logging.debug(f"Envoi du message StatusNotification: {status_notification_message}")
            await ws.send(status_notification_message)
            response = await ws.recv()
            logging.info(f"Réponse StatusNotification reçue: {response}")

            # Test StartTransaction
            start_transaction_message = json.dumps([
                2,
                "uniqueId789",
                "StartTransaction",
                {
                    "connectorId": 1,
                    "idTag": "test_id_tag",
                    "meterStart": 0,
                    "timestamp": "2023-01-01T00:00:00Z"
                }
            ])
            logging.debug(f"Envoi du message StartTransaction: {start_transaction_message}")
            await ws.send(start_transaction_message)
            response = await ws.recv()
            logging.info(f"Réponse StartTransaction reçue: {response}")

            # Test StopTransaction
            stop_transaction_message = json.dumps([
                2,
                "uniqueId101112",
                "StopTransaction",
                {
                    "transactionId": 1,
                    "meterStop": 100,
                    "timestamp": "2023-01-01T01:00:00Z"
                }
            ])
            logging.debug(f"Envoi du message StopTransaction: {stop_transaction_message}")
            await ws.send(stop_transaction_message)
            response = await ws.recv()
            logging.info(f"Réponse StopTransaction reçue: {response}")

            # Test Heartbeat
            heartbeat_message = json.dumps([
                2,
                "uniqueIdHeartbeat",
                "Heartbeat",
                {}
            ])
            logging.debug(f"Envoi du message Heartbeat: {heartbeat_message}")
            await ws.send(heartbeat_message)
            response = await ws.recv()
            logging.info(f"Réponse Heartbeat reçue: {response}")

            # Test Meter Values
            meter_values_message = json.dumps([
                2,
                "uniqueIdMeterValues",
                "MeterValues",
                {
                    "connectorId": 1,
                    "meterValue": [
                        {
                            "timestamp": "2023-01-01T00:00:00Z",
                            "sampledValue": [
                                {
                                    "value": "0",
                                    "context": "Sample.Periodic",
                                    "format": "Raw",
                                    "measurand": "Energy.Active.Import.Register",
                                    "unit": "Wh"
                                }
                            ]
                        }
                    ]
                }
            ])
            logging.debug(f"Envoi du message Meter Values: {meter_values_message}")
            await ws.send(meter_values_message)
            response = await ws.recv()
            logging.info(f"Réponse Meter Values reçue: {response}")

            # Test Authorize
            authorize_message = json.dumps([
                2,
                "uniqueIdAuthorize",
                "Authorize",
                {
                    "idTag": "test_id_tag"
                }
            ])
            logging.debug(f"Envoi du message Authorize: {authorize_message}")
            await ws.send(authorize_message)
            response = await ws.recv()
            logging.info(f"Réponse Authorize reçue: {response}")

            # Test Unlock Connector
            unlock_connector_message = json.dumps([
                2,
                "uniqueIdUnlockConnector",
                "UnlockConnector",
                {
                    "connectorId": 1
                }
            ])
            logging.debug(f"Envoi du message Unlock Connector: {unlock_connector_message}")
            await ws.send(unlock_connector_message)
            response = await ws.recv()
            logging.info(f"Réponse Unlock Connector reçue: {response}")

            # Test Remote Start Transaction
            remote_start_transaction_message = json.dumps([
                2,
                "uniqueIdRemoteStartTransaction",
                "RemoteStartTransaction",
                {
                    "idTag": "test_id_tag",
                    "connectorId": 1
                }
            ])
            logging.debug(f"Envoi du message Remote Start Transaction: {remote_start_transaction_message}")
            await ws.send(remote_start_transaction_message)
            response = await ws.recv()
            logging.info(f"Réponse Remote Start Transaction reçue: {response}")

            # Test Remote Stop Transaction
            remote_stop_transaction_message = json.dumps([
                2,
                "uniqueIdRemoteStopTransaction",
                "RemoteStopTransaction",
                {
                    "transactionId": 1
                }
            ])
            logging.debug(f"Envoi du message Remote Stop Transaction: {remote_stop_transaction_message}")
            await ws.send(remote_stop_transaction_message)
            response = await ws.recv()
            logging.info(f"Réponse Remote Stop Transaction reçue: {response}")

            # Test Get Configuration
            get_configuration_message = json.dumps([
                2,
                "uniqueIdGetConfiguration",
                "GetConfiguration",
                {
                    "key": ["key1", "key2"]
                }
            ])
            logging.debug(f"Envoi du message Get Configuration: {get_configuration_message}")
            await ws.send(get_configuration_message)
            response = await ws.recv()
            logging.info(f"Réponse Get Configuration reçue: {response}")

    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket: {e}")

asyncio.run(test_websocket())