# 🔐 Using Azure Key Vault for Secrets

## Purpose:
Store your `COSMOS_ENDPOINT` and `COSMOS_KEY` securely.

## Steps:
1. Create a Key Vault in the Azure Portal.
2. Add secrets named:
   - `COSMOS_ENDPOINT`
   - `COSMOS_KEY`
3. In your Function App:
   - Enable "Managed Identity"
   - Assign access policy in Key Vault
4. Modify your Azure Function to fetch secrets using `azure-identity` and `azure-keyvault-secrets`.

## Python Sample:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault_url = "https://<your-keyvault-name>.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)

COSMOS_ENDPOINT = client.get_secret("COSMOS_ENDPOINT").value
COSMOS_KEY = client.get_secret("COSMOS_KEY").value
```
