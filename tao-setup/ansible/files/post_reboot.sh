#!/bin/bash
set -e

# Setup Tao daemon
cd ~/TAO-poc/tao-setup
chmod +x scripts/setup-daemon.sh
make setup-daemon

# Start services and initialize
docker compose up -d
sleep 300  # Wait 5 mins for services to initialize
make setup-tao