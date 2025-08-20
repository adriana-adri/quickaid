import azure.functions as func
import json
import os
import uuid
import logging
from datetime import datetime
from azure.cosmos import CosmosClient

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize Key Vault client 
VAULT_URL = "https://quickaid.vault.azure.net/"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        email = req.params.get("email")
        # Get secrets from Key Vault
        cosmos_endpoint = secret_client.get_secret("CosmosEndpoint").value
        cosmos_key = secret_client.get_secret("CosmosKey").value
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        db = client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")

        query = f"SELECT * FROM Tickets t WHERE t.email = '{email}'" if email else "SELECT * FROM Tickets t"
        tickets = list(container.query_items(query=query, enable_cross_partition_query=True))

        return func.HttpResponse(json.dumps(tickets), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
