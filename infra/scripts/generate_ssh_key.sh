#!/bin/bash

# Default key path
KEY_PATH="$HOME/.ssh/azure_key"

# Function to display script usage
usage() {
    echo "Usage: $0 [-p path/to/key]"
    echo "Generates SSH key pair for Azure VM access"
    echo ""
    echo "Options:"
    echo "  -p    Specify custom path for the SSH key (default: $KEY_PATH)"
    echo "  -h    Display this help message"
}

# Process command line options
while getopts "p:h" opt; do
    case $opt in
        p)
            KEY_PATH="$OPTARG"
            ;;
        h)
            usage
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            exit 1
            ;;
    esac
done

# Create .ssh directory if it doesn't exist
mkdir -p "$(dirname "$KEY_PATH")"

# Check if key already exists
if [ -f "$KEY_PATH" ]; then
    echo "Warning: SSH key already exists at $KEY_PATH"
    read -p "Do you want to overwrite it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Existing key was not overwritten."
        exit 1
    fi
fi

# Generate SSH key pair
echo "Generating SSH key pair..."
ssh-keygen -t rsa -b 4096 -f "$KEY_PATH" -N "" -C "azure-vm-$(date +%Y%m%d)"

# Set appropriate permissions
chmod 600 "$KEY_PATH"
chmod 644 "$KEY_PATH.pub"

echo
echo "SSH key pair generated successfully:"
echo "Private key: $KEY_PATH"
echo "Public key:  $KEY_PATH.pub"
echo
echo "Add the following to your terraform.tfvars file:"
echo "ssh_key_path = \"$KEY_PATH.pub\""