import azure.functions as func
import json
import os
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        email = req.params.get("email")
        endpoint = os.environ["COSMOS_ENDPOINT"]
        key = os.environ["COSMOS_KEY"]
        client = CosmosClient(endpoint, key)
        db = client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")

        query = f"SELECT * FROM Tickets t WHERE t.email = '{email}'" if email else "SELECT * FROM Tickets t"
        tickets = list(container.query_items(query=query, enable_cross_partition_query=True))

        return func.HttpResponse(json.dumps(tickets), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
