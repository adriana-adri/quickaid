import azure.functions as func
import json
import os
import uuid
from azure.cosmos import CosmosClient
import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

message = Mail(
from_email='support@yourdomain.com',
to_emails=data["email"],
subject='QuickAid Ticket Submitted',
html_content=f"Hi, your ticket '{data['title']}' has been received."
)
sg.send(message)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        ticket = {
            "id": str(uuid.uuid4()),
            "title": data.get("title"),
            "email": data.get("email"),
            "category": data.get("category"),
            "description": data.get("description"),
            "status": "New"
        }

        endpoint = os.environ["COSMOS_ENDPOINT"]
        key = os.environ["COSMOS_KEY"]
        client = CosmosClient(endpoint, key)
        db = client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")
        container.create_item(body=ticket)

        return func.HttpResponse(json.dumps({"message": "Ticket submitted", "id": ticket["id"]}),
                                 status_code=200,
                                 mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
