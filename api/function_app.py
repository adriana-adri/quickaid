import azure.functions as func
import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize Azure Function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Configure Key Vault connection
vault_url = "https://quickaid.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve secrets from Key Vault
COSMOS_ENDPOINT = client.get_secret("COSMOS_ENDPOINT").value
COSMOS_KEY = client.get_secret("COSMOS_KEY").value
SENDGRID_API_KEY = client.get_secret("SENDGRID_API_KEY").value

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        logging.info("Ticket submitted successfully")  # Added logging
        return func.HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully. "
            f"Using COSMOS_ENDPOINT: {COSMOS_ENDPOINT}"
        )
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. "
            "Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
