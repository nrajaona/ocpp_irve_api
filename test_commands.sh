#!/bin/bash

echo "Testing /start endpoint:"
curl -X POST http://localhost:8001/start
echo -e "\n"

echo "Testing /stop endpoint:"
curl -X POST http://localhost:8001/stop
echo -e "\n"

echo "Testing /status endpoint:"
curl -X GET http://localhost:8001/status
echo -e "\n"
