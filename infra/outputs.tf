# Output the resource group name
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

# Output the VM name
output "vm_name" {
  description = "Name of the virtual machine"
  value       = azurerm_linux_virtual_machine.vm.name
}

# Output location
output "location" {
  description = "Location of the deployment"
  value       = azurerm_resource_group.rg.location
}

# Output the public IP address
output "public_ip_address" {
  description = "Public IP Address of the VM"
  value       = azurerm_public_ip.public_ip.ip_address
  depends_on  = [azurerm_public_ip.public_ip]
}

# Output VM size
output "vm_size" {
  description = "Size of the virtual machine"
  value       = azurerm_linux_virtual_machine.vm.size
}

# Output SSH connection string
output "ssh_connection" {
  description = "Command to connect to the VM via SSH"
  value       = "ssh -i ~/.ssh/azure_key ${var.admin_username}@${azurerm_public_ip.public_ip.ip_address}"
  depends_on  = [azurerm_public_ip.public_ip]
}