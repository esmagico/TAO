## Steps to follow:

## Prereqisite 

1. Git
2. Ansible
3. Terraform
4. Azure CLI
5. Python 3.10+


# Step 1:
**Make sure you are in infra directory**
 - Refer to the instructions present in the infra/README.md


# Step 2
 - Create A type DNS record for your domain with the public ip of the VM you created.

# Step 3:
**Make sure you are in tao-setup directory**
```
cd tao-setup
```

**First copy .env.example to .env**

```bash
cp .env.example .env
```

**Now edit your `.env` file.**
```bash
vim .env 
```

**To run the script**
```
./scripts/setup.sh
```
