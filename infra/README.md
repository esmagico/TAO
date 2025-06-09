## Authentication Setup

1. **Create Service Principal**
   ```bash
   # Login to Azure first
   az login

   # Get your subscription ID
   az account show --query id --output tsv

   # Create Service Principal (replace YOUR_SUBSCRIPTION_ID)
   az ad sp create-for-rbac \
      --name="terraform-sp" \
      --role="Contributor" \
      --scopes="/subscriptions/YOUR_SUBSCRIPTION_ID" \
      --query "{client_id: appId, client_secret: password}" \
      --output json

   ```


2. **Set Environment Variables**
   The command above will output credentials. Set them as environment variables:
   ```bash
   export ARM_SUBSCRIPTION_ID="your_subscription_id"
   export ARM_TENANT_ID="your_tenant_id"
   export ARM_CLIENT_ID="your_client_id"
   export ARM_CLIENT_SECRET="your_client_secret"
   ```

   Pro tip: Add these to your ~/.bashrc or ~/.profile to make them permanent:
   ```bash
   echo 'export ARM_SUBSCRIPTION_ID="your_subscription_id"' >> ~/.bashrc
   echo 'export ARM_TENANT_ID="your_tenant_id"' >> ~/.bashrc
   echo 'export ARM_CLIENT_ID="your_client_id"' >> ~/.bashrc
   echo 'export ARM_CLIENT_SECRET="your_client_secret"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Quick Start

1. **Run the setup script**
   ```bash
   # Make the script executable
   chmod +x scripts/setup.sh

   # Run the setup script
   ./scripts/setup.sh
   ```
   This script will:
   - Verify service principal credentials
   - Generate SSH key pair if not exists
   - Create terraform.tfvars with credentials
   - Initialize Terraform

2. **Deploy the VM**
   ```bash
   # Plan the deployment
   terraform plan

   # Apply the configuration
   terraform apply
   ```

3. **SSH into the server**

   From the output of `terraform apply`command use the ssh command displayed into the server to ssh into the instance (make sure you ignore quotes.). 

   ```bash
      ssh -i ~/.ssh/azure_key azureuser@4.247.156.0
   ```

4. After SSH install Docker on remote server by following commands

   ```
      # Add Docker's official GPG key:
      sudo apt-get update
      sudo apt-get install ca-certificates curl
      sudo install -m 0755 -d /etc/apt/keyrings
      sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
      sudo chmod a+r /etc/apt/keyrings/docker.asc

      # Add the repository to Apt sources:
      echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      sudo apt-get update

      sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

      sudo usermod -aG docker ${USER}
   ```



