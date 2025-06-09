#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Preamble: Determine paths and check prerequisites ---
echo "▶ Initializing setup..."

# Get the directory where this script is located
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
# The project root is one level up from the script's directory
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# Define key file paths relative to the project root
PLAYBOOK_PATH="${PROJECT_ROOT}/ansible/setup_tao.yml"
ENV_FILE="${PROJECT_ROOT}/.env"

# 1. Check if ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo "❌ Error: ansible-playbook could not be found."
    echo "Please install Ansible first: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html"
    exit 1
fi

# 2. Check if .env file exists
if [ ! -f "${ENV_FILE}" ]; then
    echo "❌ Error: ${ENV_FILE} not found."
    echo "Please 'cd tao-setup', copy .env.example to .env, and fill in your details."
    exit 1
fi

# Load environment variables from .env file
source "${ENV_FILE}"
echo "✔ Prerequisites met. Configuration loaded from .env file."
echo

# --- Main Execution ---

# Define paths for temporary files, which will be created alongside this script
TEMP_INVENTORY="${SCRIPT_DIR}/temp_inventory"
TEMP_VAULT_PASS_FILE="${SCRIPT_DIR}/temp_vault_pass"

# This 'trap' command ensures our temporary files are deleted when the script exits
trap 'echo; echo "▶ Cleaning up temporary files..."; rm -f "$TEMP_INVENTORY" "$TEMP_VAULT_PASS_FILE"' EXIT

echo "▶ Generating temporary Ansible configuration..."

# 1. Create temporary inventory file from .env variables
#    THIS IS THE CORRECTED LINE:
cat << EOF > "$TEMP_INVENTORY"
[tao_servers]
server1 ansible_host=${SERVER_IP} ansible_user=${REMOTE_USER} ansible_ssh_private_key_file=${SSH_KEY_PATH}
EOF
echo "✔ Temporary inventory file created."

# 2. Create temporary vault password file from .env variable
echo "${ANSIBLE_VAULT_PASSWORD}" > "$TEMP_VAULT_PASS_FILE"
chmod 600 "$TEMP_VAULT_PASS_FILE" # Set strict permissions
echo "✔ Temporary vault password file created."
echo

echo "▶ Running Ansible Playbook..."
echo "-----------------------------------"

# Run the playbook using the defined paths
ansible-playbook \
    -i "${TEMP_INVENTORY}" \
    --vault-password-file "${TEMP_VAULT_PASS_FILE}" \
    -e "github_user=${GITHUB_USER}" \
    -e "github_pat=${GITHUB_PAT}" \
    "${PLAYBOOK_PATH}"

echo "-----------------------------------"
echo "✅ Playbook finished successfully!"
# The trap will now execute automatically to clean up.
