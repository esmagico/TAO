# Azure Provider Authentication Variables
variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "azure_tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "azure_client_id" {
  description = "Azure Client ID (Service Principal)"
  type        = string
}

variable "azure_client_secret" {
  description = "Azure Client Secret (Service Principal)"
  type        = string
  sensitive   = true
}

# Azure Provider Configuration Variables
variable "location" {
  description = "The Azure region where resources will be created"
  type        = string
  default     = "centralindia"
}

# Resource Group Variables
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "simple-vm-rg-10"
}

# Virtual Machine Variables
variable "vm_name" {
  description = "Name of the virtual machine"
  type        = string
  default     = "simple-vm-10"
}

variable "vm_size" {
  description = "Size of the virtual machine (default: 2 CPU, 4GB RAM)"
  type        = string
  default     = "Standard_B2s"
}

variable "admin_username" {
  description = "Username for the VM admin account"
  type        = string
  default     = "azureuser"
}

variable "ssh_key_path" {
  description = "Path to the public SSH key"
  type        = string
  default     = "~/.ssh/azure_key.pub"
}

# Network Variables
variable "vnet_name" {
  description = "Name of the virtual network"
  type        = string
  default     = "simple-vnet-10"
}

variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
  default     = "simple-subnet-10"
}

variable "nsg_name" {
  description = "Name of the network security group"
  type        = string
  default     = "simple-nsg-10"
}

# OS Variables
variable "os_disk_size" {
  description = "Size of the OS disk in GB"
  type        = number
  default     = 30
}

variable "os_publisher" {
  description = "Publisher of the OS image"
  type        = string
  default     = "Canonical"
}

variable "os_offer" {
  description = "Offer of the OS image"
  type        = string
  default     = "0001-com-ubuntu-server-jammy"  # Ubuntu 22.04 LTS
}

variable "os_sku" {
  description = "SKU of the OS image"
  type        = string
  default     = "22_04-lts"  # Ubuntu 22.04 LTS
}

variable "os_version" {
  description = "Version of the OS image"
  type        = string
  default     = "latest"
}