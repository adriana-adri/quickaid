from flask import Flask, request, jsonify, send_from_directory
import json
import os
import uuid
from azure.cosmos import CosmosClient

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Azure Cosmos DB configuration
endpoint = os.environ.get("COSMOS_ENDPOINT")
key = os.environ.get("COSMOS_KEY")

if endpoint and key:
    client = CosmosClient(endpoint, key)
    db = client.get_database_client("QuickAidDB")
    container = db.get_container_client("Tickets")

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/api/submit_ticket', methods=['POST'])
def submit_ticket():
    try:
        data = request.get_json()
        ticket = {
            "id": str(uuid.uuid4()),
            "title": data.get("title"),
            "email": data.get("email"),
            "category": data.get("category"),
            "description": data.get("description"),
            "status": "New"
        }

        if endpoint and key:
            container.create_item(body=ticket)
        else:
            # For testing without Cosmos DB
            print(f"Would create ticket: {ticket}")

        return jsonify({"message": "Ticket submitted", "id": ticket["id"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_tickets', methods=['GET'])
def get_tickets():
    try:
        email = request.args.get("email")
        
        if endpoint and key:
            query = f"SELECT * FROM Tickets t WHERE t.email = '{email}'" if email else "SELECT * FROM Tickets t"
            tickets = list(container.query_items(query=query, enable_cross_partition_query=True))
        else:
            # For testing without Cosmos DB
            tickets = []

        return jsonify(tickets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
