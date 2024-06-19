from fastapi import APIRouter, Query, Body
import websockets
import asyncio
import logging
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel, Field
from typing import Optional, List


router = APIRouter()

load_dotenv()
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL_LOCALHOST")
  

class StatusResponse(BaseModel):
    connectorId: int = Field(..., description="ID du connecteur")
    errorCode: str = Field(..., description="Code d'erreur", example="NoError")
    status: str = Field(..., description="Statut du connecteur", example="Available")
    timestamp: str = Field(..., description="Horodatage de la réponse", example="2023-05-21T15:00:00Z")
    info: Optional[str] = Field(None, description="Informations supplémentaires", example="Test")
    vendorId: Optional[str] = Field(None, description="ID du fournisseur", example="Vendor")
    vendorErrorCode: Optional[str] = Field(None, description="Code d'erreur fournisseur", example="NoError")

class StartChargingResponse(BaseModel):
    message: str = Field(..., description="Message indiquant le début de la charge", example="Charging started")
    error: Optional[str] = Field(None, description="Message d'erreur, le cas échéant", example="Error message")

class StopChargingResponse(BaseModel):
    message: str = Field(..., description="Message indiquant l'arrêt de la charge", example="Charging stopped")
    error: Optional[str] = Field(None, description="Message d'erreur, le cas échéant", example="Error message")

class HeartbeatResponse(BaseModel):
    current_time: str

class MeterValuesResponse(BaseModel):
    meter_value: dict

class AuthorizeRequest(BaseModel):
    id_tag: str

class AuthorizeResponse(BaseModel):
    id_tag_info: dict

class UnlockConnectorRequest(BaseModel):
    connector_id: int

class UnlockConnectorResponse(BaseModel):
    status: Optional[str] = None
    error: Optional[str] = None

class RemoteStartTransactionRequest(BaseModel):
    id_tag: str
    connector_id: Optional[int] = None

class RemoteStartTransactionResponse(BaseModel):
    status: Optional[str] = None
    error: Optional[str] = None

class RemoteStopTransactionRequest(BaseModel):
    transaction_id: int

class RemoteStopTransactionResponse(BaseModel):
    status: Optional[str] = None
    error: Optional[str] = None

class GetConfigurationRequest(BaseModel):
    key: Optional[List[str]] = None

class GetConfigurationResponse(BaseModel):
    configuration_key: Optional[List[dict]] = None
    unknown_key: Optional[List[str]] = None
    error: Optional[str] = None

class ChangeConfigurationRequest(BaseModel):
    key: str
    value: str

class ChangeConfigurationResponse(BaseModel):
    status: Optional[str] = None
    error: Optional[str] = None

async def send_command(message: str):
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as websocket:
            logging.info(f"Envoi de la commande: {message}")
            await websocket.send(message)
            response = await websocket.recv()
            logging.info(f"Réponse reçue: {response}")
            return json.loads(response)  # Assurez-vous de retourner la réponse sous forme de dictionnaire
    except Exception as e:
        logging.error(f"Erreur de connexion WebSocket: {e}")
        return {"error": str(e)}

@router.get("/test-websocket", summary="Tester la connexion WebSocket", description="Ce endpoint permet de tester la connexion WebSocket avec le serveur de gestion des points de charge. Il envoie un message de `BootNotification` au serveur pour vérifier si la connexion est correctement établie et si le serveur répond comme attendu. Ce message inclut des informations de base sur le modèle et le fournisseur du point de charge, extraites des variables d'environnement configurées. Ce test est essentiel pour valider la communication initiale entre le point de charge et le serveur central.")
async def test_websocket_endpoint(
    charge_point_vendor: str = Query(os.getenv("CHARGE_POINT_VENDOR", "Vendor_Y"), description="Le fournisseur du point de charge"),
    charge_point_model: str = Query(os.getenv("CHARGE_POINT_MODEL", "Model_X"), description="Le modèle du point de charge")
):
    """
    Teste la connexion WebSocket avec un message BootNotification.

    - **chargePointVendor**: Le fournisseur du point de charge
    - **chargePointModel**: Le modèle du point de charge
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie")
            boot_notification_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueId123",  # Unique ID for the message
                "BootNotification",  # Action
                {
                    "chargePointVendor": charge_point_vendor,
                    "chargePointModel": charge_point_model
                }
            ])
            await ws.send(boot_notification_message)
            response = await ws.recv()
            logging.info(f"Réponse reçue: {response}")
            return {"message": response}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket: {e}")
        return {"error": str(e)}


@router.get("/status", summary="Récupérer le statut actuel du connecteur", description="Ce endpoint permet de récupérer des informations détaillées sur le statut actuel d'un connecteur de charge. Il envoie un message `StatusNotification` au serveur via WebSocket pour obtenir le statut en temps réel. La réponse inclut des détails tels que l'ID du connecteur, le code d'erreur, le statut (par exemple, disponible ou occupé), un horodatage, ainsi que des informations supplémentaires fournies par le fournisseur du point de charge. Cette fonctionnalité est cruciale pour surveiller et diagnostiquer l'état opérationnel des points de charge.", response_model=StatusResponse)
async def get_status(
    connector_id: int = Query(1, description="L'identifiant du connecteur"),
    error_code: str = Query("NoError", description="Code d'erreur"),
    status: str = Query("Available", description="Statut actuel du connecteur"),
    timestamp: str = Query("2023-05-21T15:00:00Z", description="Horodatage de la requête"),
    info: Optional[str] = Query("Additional information about the status", description="Informations supplémentaires"),
    vendor_id: Optional[str] = Query("Vendor123", description="Identifiant du fournisseur"),
    vendor_error_code: Optional[str] = Query("VendorError456", description="Code d'erreur spécifique au fournisseur")
):
    """
    Récupère le statut actuel du connecteur avec des informations détaillées.

    - **connectorId**: L'identifiant du connecteur
    - **errorCode**: Code d'erreur (NoError si tout va bien)
    - **status**: Statut actuel (Available, Occupied, etc.)
    - **timestamp**: Horodatage de la requête
    - **info**: Informations supplémentaires
    - **vendorId**: Identifiant du fournisseur
    - **vendorErrorCode**: Code d'erreur spécifique au fournisseur
    """
    try:
        payload = {
            "connectorId": connector_id,
            "errorCode": error_code,
            "status": status,
            "timestamp": timestamp,
            "info": info,
            "vendorId": vendor_id,
            "vendorErrorCode": vendor_error_code
        }
        message = json.dumps([2, "uniqueId123", "StatusNotification", payload])
        response = await send_command(message)
        
        # Assurez-vous que la réponse est un dictionnaire conforme au modèle
        return payload
    except Exception as e:
        return {"error": str(e)}

@router.post("/start", summary="Démarrer une session de charge", description="Ce endpoint initie une session de charge pour un véhicule électrique en envoyant un message `StartTransaction` au serveur. Les paramètres incluent l'ID du connecteur, l'identifiant de la carte RFID (`idTag`) utilisée pour authentifier la session de charge, la valeur initiale du compteur électrique (`meterStart`), et un horodatage. Ce processus démarre officiellement la transaction de charge, permettant au véhicule de commencer à recevoir de l'énergie. La réponse du serveur indiquera si la session a été démarrée avec succès et fournira des détails supplémentaires si nécessaire.")
async def start_charging(
    connector_id: int = Query(1, description="L'identifiant du connecteur"),
    id_tag: str = Query("ABC123", description="Identifiant de la carte RFID"),
    meter_start: int = Query(0, description="Valeur initiale du compteur"),
    timestamp: str = Query("2023-05-21T15:00:00Z", description="Horodatage de la requête")
):
    """
    Démarre une session de charge.

    - **connectorId**: L'identifiant du connecteur
    - **idTag**: Identifiant de la carte RFID
    - **meterStart**: Valeur initiale du compteur
    - **timestamp**: Horodatage de la requête
    """
    try:
        payload = {
            "connectorId": connector_id,
            "idTag": id_tag,
            "meterStart": meter_start,
            "timestamp": timestamp
        }
        message = json.dumps([2, "uniqueId123", "StartTransaction", payload])
        response = await send_command(message)
        return {"message": f"Charging started for {response}"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/stop", summary="Arrêter une session de charge", description="Ce endpoint arrête une session de charge en cours pour un véhicule électrique en envoyant un message `StopTransaction` au serveur. Les paramètres incluent l'ID de la transaction en cours, la valeur finale du compteur électrique (`meterStop`), et un horodatage. Cette action met fin à la transaction de charge, et la réponse du serveur fournira des détails sur la session de charge terminée.")
async def stop_charging(
    transaction_id: int = Query(1, description="L'identifiant de la transaction"),
    meter_stop: int = Query(10, description="Valeur finale du compteur"),
    timestamp: str = Query("2023-05-21T16:00:00Z", description="Horodatage de la requête")
):
    """
    Arrête une session de charge.

    - **transactionId**: L'identifiant de la transaction
    - **meterStop**: Valeur finale du compteur
    - **timestamp**: Horodatage de la requête
    """
    try:
        payload = {
            "transactionId": transaction_id,
            "meterStop": meter_stop,
            "timestamp": timestamp
        }
        message = json.dumps([2, "uniqueId123", "StopTransaction", payload])
        response = await send_command(message)
        return {"message": f"Charging stopped for {response}"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/heartbeat", response_model=HeartbeatResponse, summary="Envoyer un Heartbeat", description="Ce endpoint envoie un message Heartbeat au serveur via WebSocket pour vérifier la connexion.")
async def heartbeat():
    """
    Envoie un message Heartbeat au serveur via WebSocket.

    - **current_time**: L'heure actuelle renvoyée par le serveur
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Heartbeat")
            heartbeat_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueIdHeartbeat",  # Unique ID for the message
                "Heartbeat",  # Action
                {}
            ])
            await ws.send(heartbeat_message)
            response = await ws.recv()
            logging.info(f"Réponse Heartbeat reçue: {response}")
            return {"current_time": json.loads(response)[2]["currentTime"]}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Heartbeat: {e}")
        return {"error": str(e)}
    
@router.post("/meter-values", response_model=MeterValuesResponse, summary="Envoyer des valeurs de compteur", description="Ce endpoint envoie des valeurs de compteur au serveur via WebSocket.")
async def meter_values():
    """
    Envoie des valeurs de compteur au serveur via WebSocket.

    - **meter_value**: Les valeurs de compteur renvoyées par le serveur
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Meter Values")
            meter_values_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueIdMeterValues",  # Unique ID for the message
                "MeterValues",  # Action
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
            await ws.send(meter_values_message)
            response = await ws.recv()
            logging.info(f"Réponse Meter Values reçue: {response}")
            return {"meter_value": json.loads(response)[2]}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Meter Values: {e}")
        return {"error": str(e)}
    
@router.post("/authorize", response_model=AuthorizeResponse, summary="Autoriser un utilisateur", description="Ce endpoint envoie une demande d'autorisation au serveur via WebSocket.")
async def authorize(
    request: AuthorizeRequest = Body(..., description="Requête d'autorisation contenant l'identifiant de la carte RFID")
):
    """
    Envoie une demande d'autorisation au serveur via WebSocket.

    - **idTag**: Identifiant de la carte RFID
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Authorize")
            authorize_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueIdAuthorize",  # Unique ID for the message
                "Authorize",  # Action
                {
                    "idTag": request.id_tag
                }
            ])
            await ws.send(authorize_message)
            response = await ws.recv()
            logging.info(f"Réponse Authorize reçue: {response}")
            return {"id_tag_info": json.loads(response)[2]}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Authorize: {e}")
        return {"error": str(e)}
    
@router.post("/unlock-connector", response_model=UnlockConnectorResponse, summary="Déverrouiller un connecteur", description="Ce endpoint envoie une demande de déverrouillage de connecteur au serveur via WebSocket.")
async def unlock_connector(
    request: UnlockConnectorRequest = Body(..., description="Requête de déverrouillage contenant l'identifiant du connecteur")
):
    """
    Envoie une demande de déverrouillage de connecteur au serveur via WebSocket.

    - **connectorId**: Identifiant du connecteur à déverrouiller
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Unlock Connector")
            unlock_connector_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueIdUnlockConnector",  # Unique ID for the message
                "UnlockConnector",  # Action
                {
                    "connectorId": request.connector_id
                }
            ])
            await ws.send(unlock_connector_message)
            response = await ws.recv()
            logging.info(f"Réponse Unlock Connector reçue: {response}")
            response_data = json.loads(response)
            if response_data[0] == 4:  # MessageTypeId (4 = CALLERROR)
                return {"error": response_data[2]}
            return {"status": response_data[2].get("status")}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Unlock Connector: {e}")
        return {"error": str(e)}
    
@router.post("/remote-start-transaction", response_model=RemoteStartTransactionResponse, summary="Démarrer une transaction à distance", description="Ce endpoint envoie une demande de démarrage de transaction à distance au serveur via WebSocket.")
async def remote_start_transaction(
    request: RemoteStartTransactionRequest = Body(..., description="Requête de démarrage de transaction contenant l'identifiant de la carte RFID et éventuellement l'identifiant du connecteur")
):
    """
    Envoie une demande de démarrage de transaction à distance au serveur via WebSocket.

    - **idTag**: Identifiant de la carte RFID
    - **connectorId**: (Optionnel) Identifiant du connecteur 
    """ 
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Remote Start Transaction")
            remote_start_transaction_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueIdRemoteStartTransaction",  # Unique ID for the message
                "RemoteStartTransaction",  # Action
                {
                    "idTag": request.id_tag,
                    "connectorId": request.connector_id
                }
            ])
            await ws.send(remote_start_transaction_message)
            response = await ws.recv()
            logging.info(f"Réponse Remote Start Transaction reçue: {response}")
            response_data = json.loads(response)
            if response_data[0] == 4:  # MessageTypeId (4 = CALLERROR)
                return {"error": response_data[2]}
            return {"status": response_data[2].get("status")}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Remote Start Transaction: {e}")
        return {"error": str(e)}
    
@router.post("/remote-stop-transaction", response_model=RemoteStopTransactionResponse, summary="Arrêter une transaction à distance", description="Ce endpoint envoie une demande d'arrêt de transaction à distance au serveur via WebSocket.")
async def remote_stop_transaction(
    request: RemoteStopTransactionRequest = Body(..., description="Requête d'arrêt de transaction contenant l'identifiant de la transaction")
):
    """
    Envoie une demande d'arrêt de transaction à distance au serveur via WebSocket.

    - **transactionId**: Identifiant de la transaction à arrêter
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Remote Stop Transaction")
            remote_stop_transaction_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueIdRemoteStopTransaction",  # Unique ID for the message
                "RemoteStopTransaction",  # Action
                {
                    "transactionId": request.transaction_id
                }
            ])
            await ws.send(remote_stop_transaction_message)
            response = await ws.recv()
            logging.info(f"Réponse Remote Stop Transaction reçue: {response}")
            response_data = json.loads(response)
            if response_data[0] == 4:  # MessageTypeId (4 = CALLERROR)
                return {"error": response_data[2]}
            return {"status": response_data[2].get("status")}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Remote Stop Transaction: {e}")
        return {"error": str(e)}
    
@router.post("/get-configuration", response_model=GetConfigurationResponse, summary="Obtenir la configuration", description="Ce endpoint envoie une demande pour obtenir la configuration de la station de charge via WebSocket.")
async def get_configuration(
    request: GetConfigurationRequest = Body(..., description="Requête pour obtenir la configuration contenant éventuellement une liste de clés")
):
    """
    Envoie une demande pour obtenir la configuration de la station de charge via WebSocket.

    - **key**: (Optionnel) Liste des clés de configuration à obtenir
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Get Configuration")
            get_configuration_message = json.dumps([
                2,  # MessageTypeId (2 = CALL)
                "uniqueIdGetConfiguration",  # Unique ID for the message
                "GetConfiguration",  # Action
                {
                    "key": request.key
                }
            ])
            await ws.send(get_configuration_message)
            response = await ws.recv()
            logging.info(f"Réponse Get Configuration reçue: {response}")
            response_data = json.loads(response)
            if response_data[0] == 4:  # MessageTypeId (4 = CALLERROR)
                return {"error": response_data[2]}
            return {
                "configuration_key": response_data[2].get("configurationKey"),
                "unknown_key": response_data[2].get("unknownKey")
            }
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Get Configuration: {e}")
        return {"error": str(e)}
    
@router.post("/change-configuration", response_model=ChangeConfigurationResponse, summary="Changer la configuration", description="Ce endpoint envoie une demande de changement de configuration au serveur via WebSocket.")
async def change_configuration_endpoint(
    request: ChangeConfigurationRequest = Body(..., description="Requête de changement de configuration contenant la clé et la valeur")
):
    """
    Envoie une demande de changement de configuration au serveur via WebSocket.

    - **key**: Clé de configuration à changer
    - **value**: Nouvelle valeur pour la clé de configuration
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, subprotocols=["ocpp1.6"]) as ws:
            logging.info("Connexion WebSocket établie pour Change Configuration")
            response = await change_configuration(ws, request.key, request.value)
            if "error" in response:
                return {"error": response["error"]}
            return {"status": response.get("status")}
    except Exception as e:
        logging.error(f"Erreur lors de la connexion WebSocket pour Change Configuration: {e}")
        return {"error": str(e)}