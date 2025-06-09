#!/bin/bash
source ~/TAO-poc/tao-setup/.env

CONTAINER_NAME=tao-1  # Update to your actual container name
TARGET_URL="http://${SERVER_IP}:8080/"
CONFIG_PATH="/var/www/html/config/generis.conf.php"

# Start container if it's not already running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container $CONTAINER_NAME is not running. Starting it..."
    docker start "$CONTAINER_NAME"
    sleep 5  # Give it a moment to initialize
else
    echo "Container $CONTAINER_NAME is already running."
fi

echo "Waiting for generis.conf.php in $CONTAINER_NAME..."

for i in {1..90}; do
    docker exec "$CONTAINER_NAME" test -f "$CONFIG_PATH" && break
    sleep 5
done

if ! docker exec "$CONTAINER_NAME" test -f "$CONFIG_PATH"; then
    echo "❌ Timeout: config file not found in $CONTAINER_NAME"
    exit 1
fi

echo "Patching ROOT_URL..."
docker exec "$CONTAINER_NAME" sed -i "s|define('ROOT_URL'.*|define('ROOT_URL','${TARGET_URL}');|" "$CONFIG_PATH"

echo "✅ ROOT_URL updated"

# Restart the container to apply changes
echo "🔄 Restarting container $CONTAINER_NAME..."
docker restart "$CONTAINER_NAME"

echo "✅ Container $CONTAINER_NAME restarted"
