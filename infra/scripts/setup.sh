#!/bin/bash

echo "Azure VM Deployment Setup Script"
echo "=============================="

# Function to check required environment variables
check_env_vars() {
    local missing_vars=0
    local required_vars=(
        "ARM_SUBSCRIPTION_ID"
        "ARM_TENANT_ID"
        "ARM_CLIENT_ID"
        "ARM_CLIENT_SECRET"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "Error: $var is not set"
            missing_vars=1
        fi
    done

    if [ $missing_vars -eq 1 ]; then
        echo """
To authenticate using a service principal, you need to set the following environment variables:
export ARM_SUBSCRIPTION_ID=\"your_subscription_id\"
export ARM_TENANT_ID=\"your_tenant_id\"
export ARM_CLIENT_ID=\"your_client_id\"
export ARM_CLIENT_SECRET=\"your_client_secret\"

You can create a service principal using:
az ad sp create-for-rbac --name \"terraform-sp\" --role=\"Contributor\" --scopes=\"/subscriptions/your_subscription_id\"

The command will output the required credentials:
{
  \"clientId\": \"...\",        # Use as ARM_CLIENT_ID
  \"clientSecret\": \"...\",    # Use as ARM_CLIENT_SECRET
  \"subscriptionId\": \"...\",  # Use as ARM_SUBSCRIPTION_ID
  \"tenantId\": \"...\"         # Use as ARM_TENANT_ID
}
"""
        exit 1
    fi
}

# Check if required environment variables are set
check_env_vars

# Generate SSH key if it doesn't exist
SSH_KEY_PATH="$HOME/.ssh/azure_key"
if [ ! -f "${SSH_KEY_PATH}.pub" ]; then
    echo "Generating new SSH key pair..."
    mkdir -p "$HOME/.ssh"
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "azure-vm-$(date +%Y%m%d)"
    chmod 600 "$SSH_KEY_PATH"
    chmod 644 "${SSH_KEY_PATH}.pub"
    echo "SSH key pair generated at: $SSH_KEY_PATH"
else
    echo "SSH key pair already exists at: $SSH_KEY_PATH"
fi

# Create terraform.tfvars file
cat > terraform.tfvars << EOL
# Authentication
azure_subscription_id = "${ARM_SUBSCRIPTION_ID}"
azure_tenant_id = "${ARM_TENANT_ID}"
azure_client_id = "${ARM_CLIENT_ID}"
azure_client_secret = "${ARM_CLIENT_SECRET}"
EOL

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

echo """
Setup completed successfully!
You can now run:
  terraform plan    # To see the execution plan
  terraform apply   # To create the infrastructure
"""