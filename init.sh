#!/bin/bash

echo "🧹 Shutting down existing containers and volumes..."
docker compose down -v

echo "🚀 Starting containers..."
docker compose up -d

echo "⏳ Waiting for MongoDB to be ready..."
sleep 10

echo "🧩 Initiating MongoDB replica set..."
docker exec -it agentic_mongo_db mongosh -u root -p 1234 --authenticationDatabase admin --eval '
rs.initiate({
    _id: "rs0",
    members: [{ _id: 0, host: "localhost:27017" }]
})
'

echo "🧩 Checking is master..."

docker exec -it agentic_mongo_db mongosh -u root -p 1234 --authenticationDatabase admin --eval "rs.isMaster()"