#!/bin/bash

set -eo pipefail

echo "Configuring docker daemon..."

if [ ! -s "/etc/docker/daemon.json" ]; then \
    sudo sh -c "echo \"{}\" > /etc/docker/daemon.json"; \
fi

if ! jq -e '.["log-driver"] == "json-file" and (.["log-opts"] | .["labels-regex"]) == "^.+" and .["max-concurrent-downloads"] == 20' /etc/docker/daemon.json >/dev/null; then

    sudo sh -c "jq '.[\"log-driver\"] =\"json-file\" | (.[\"log-opts\"] | .[\"labels-regex\"] ) = \"^.+\" | .[\"max-concurrent-downloads\"] = 20 ' /etc/docker/daemon.json > /etc/docker/daemon.json.tmp"
    
    sudo sh -c "mv -f /etc/docker/daemon.json.tmp /etc/docker/daemon.json ; chmod 0644 /etc/docker/daemon.json"

    sudo systemctl daemon-reload
    sudo systemctl restart docker
    echo "Docker daemon configured."
else
    
    echo "Docker daemon already configured. Skipping ..."
fi
