# KimikOCPP

KimikOCPP est une application qui gère les interactions avec un chargeur de véhicule électrique (EV) via le protocole OCPP (Open Charge Point Protocol). Le projet utilise un serveur de gestion central (Steve) et un simulateur de chargeur (Micro-ocpp). 

## Objectifs

- Gérer les connexions et les transactions de charge des véhicules électriques via des API.
- Fournir une interface pour interagir avec le chargeur et le serveur OCPP.

## Prérequis

- Python 3.9+
- Docker et Docker Compose
- Git

## Installation

### Cloner le projet

```sh
git clone https://github.com/votre-utilisateur/KimikOCPP.git
cd KimikOCPP
```

### Configuration des Dépendances

Installez les dépendances Python :

```sh
pip install -r requirements.txt
```

## Configuration

### Fichier .env

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```ini
# WebSocket Configuration
WEBSOCKET_URL=ws://localhost:8180/steve/websocket/CentralSystemService/charger-01
WEBSOCKET_URL_INTERNAL=ws://steve-app-1:8180/steve/websocket/CentralSystemService/charger-01
WEBSOCKET_URL_LOCALHOST=ws://localhost:8180/steve/websocket/CentralSystemService/charger-01

# Charge Point Identification
CHARGE_POINT_ID=charger-01
CHARGE_POINT_SERIAL_NUMBER=123456789

# Charge Point Details
CHARGE_POINT_MODEL=Model_X
CHARGE_POINT_VENDOR=Vendor_Y
FIRMWARE_VERSION=1.0.0

# Authentication and Security
AUTHORIZATION_KEY=your_authorization_key_here
CA_CERTIFICATE=path_to_your_ca_cert_here
TLS_VERSION=v2.3.1
TLS_EXPIRATION_DATE=2026-12-26

# Connection Settings
PING_INTERVAL=5           # Intervalle de ping en secondes
RECONNECT_INTERVAL=10     # Intervalle de reconnexion en secondes

# EVSE (Electric Vehicle Supply Equipment) Configuration
EVSE_ID=1

# Smart Charging Configuration
MAX_POWER=11000           # Puissance maximale en watts
MAX_CURRENT=0             # Courant maximal en ampères

# Network Configuration
WIFI_NAME=company_wifi_ef3c98
WIFI_PASSWORD=your_wifi_password_here
```

### Configuration du Serveur OCPP (Steve)

1. **Cloner le dépôt Steve :**

   ```sh
   git clone https://github.com/RWTH-i5-IDSG/steve.git
   cd steve
   docker-compose up -d
   ```

2. **Accéder à l'interface web de Steve :**

   - URL : `http://localhost:8180`
   - Nom d'utilisateur : `admin`
   - Mot de passe : `1234`

3. **Ajouter une borne dans Steve :**

   - Dans l'interface web de Steve, ajoutez une nouvelle borne avec les détails suivants :
     - ID de la borne : `charger-01`
     - Modèle : `Model_X`
     - Fournisseur : `Vendor_Y`

### Configuration du Simulateur de Borne (Micro-ocpp)

1. **Cloner le dépôt Micro-ocpp :**

   ```sh
   git clone https://github.com/mobilityhouse/micro-ocpp.git
   cd micro-ocpp
   docker-compose up -d
   ```

2. **Assurez-vous que les informations de la borne correspondent à celles du fichier .env.**

## Utilisation

### Lancer l'application

Pour démarrer l'application, utilisez le script `start.sh` :

```sh
./start.sh
```

### Tester l'API

L'API peut être testée en accédant à la documentation interactive Swagger disponible à `http://localhost:8001/docs`. Notez que si l'application est exécutée dans un conteneur Docker, l'URL pourrait différer, assurez-vous de vérifier l'adresse IP et le port corrects.

## Tests

Pour exécuter les tests unitaires, utilisez pytest :

```sh
pytest
```

## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre des pull requests et ouvrir des issues pour les suggestions d'amélioration.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.