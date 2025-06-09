#!/bin/bash
set -eou pipefail

echo ">>> Updating system..."
sudo apt update -y || true
sudo apt upgrade -y || true
sudo apt-get install -y build-essential || true

echo ">>> Installing yq..."
if ! command -v yq &> /dev/null; then
  sudo wget -q https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq && \
  sudo chmod +x /usr/bin/yq
  echo "yq installed."
else
  echo "yq already installed, skipping."
fi

sudo apt install jq -y

