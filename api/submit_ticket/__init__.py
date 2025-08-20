import azure.functions as func
import json
import os
import uuid
import logging
from datetime import datetime
from azure.cosmos import CosmosClient
import sendgrid
from sendgrid.helpers.mail import Mail

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize Key Vault client 
VAULT_URL = "https://quickaid.vault.azure.net/"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)

def create_professional_email_template(ticket_data):
    """Create a professional HTML email template for ticket confirmation"""
    return f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">QuickAid Helpdesk</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Ticket Confirmation</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; border: 1px solid #e9ecef;">
            <h2 style="color: #2c3e50; margin-top: 0;">Thank you for your submission!</h2>
            <p>Your support ticket has been successfully received and assigned to our support team.</p>
            
            <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #3498db;">
                <h3 style="margin-top: 0; color: #2c3e50; font-size: 18px;">Ticket Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; color: #555; width: 120px;">Ticket ID:</td>
                        <td style="padding: 8px 0; color: #333;">{ticket_data["id"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; color: #555;">Title:</td>
                        <td style="padding: 8px 0; color: #333;">{ticket_data["title"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; color: #555;">Category:</td>
                        <td style="padding: 8px 0; color: #333;">{ticket_data["category"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; color: #555;">Status:</td>
                        <td style="padding: 8px 0;">
                            <span style="background-color: #e74c3c; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                                {ticket_data["status"]}
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; color: #555;">Submitted:</td>
                        <td style="padding: 8px 0; color: #333;">{datetime.now().strftime("%B %d, %Y at %I:%M %p")}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #856404;">📋 Issue Description:</h4>
                <p style="margin: 0; color: #856404; font-style: italic;">"{ticket_data["description"]}"</p>
            </div>
            
            <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #0c5460;">⏱️ What happens next?</h4>
                <ul style="margin: 0; padding-left: 20px; color: #0c5460;">
                    <li>Our support team will review your ticket within 2 hours</li>
                    <li>You'll receive updates via email at: <strong>{ticket_data["email"]}</strong></li>
                    <li>Expected resolution time: 24-48 hours for {ticket_data["category"]} issues</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="color: #666; margin: 0;">Need urgent assistance? Contact us:</p>
                <p style="color: #2c3e50; font-weight: bold; margin: 5px 0;">📞 (555) 123-HELP | 📧 support@quickaid.edu</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; padding: 20px; color: #6c757d; font-size: 12px; border-top: 1px solid #e9ecef;">
            <p style="margin: 0;">This is an automated message from QuickAid Helpdesk System.</p>
            <p style="margin: 5px 0 0 0;">Please do not reply to this email. For support, use the contact information above.</p>
        </div>
    </div>
    '''

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main function to handle ticket submission with professional email notifications
    """
    try:
        # Parse request body
        data = req.get_json()
        
        # Validate required fields
        required_fields = ["title", "email", "category", "description"]
        for field in required_fields:
            if not data.get(field):
                return func.HttpResponse(
                    json.dumps({"error": f"Missing required field: {field}"}),
                    status_code=400,
                    mimetype="application/json"
                )
        
        # Get secrets from Key Vault
        cosmos_endpoint = secret_client.get_secret("CosmosEndpoint").value
        cosmos_key = secret_client.get_secret("CosmosKey").value
        sendgrid_key = secret_client.get_secret("SendGridApiKey").value
        
        # Create ticket object
        ticket = {
            "id": str(uuid.uuid4()),
            "title": data.get("title"),
            "email": data.get("email"),
            "category": data.get("category"),
            "description": data.get("description"),
            "status": "New",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Save to Cosmos DB
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        db = client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")
        container.create_item(body=ticket)
        
        logging.info(f"Ticket {ticket['id']} saved to Cosmos DB successfully")

        # Send confirmation email with SendGrid
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
        
        # Create professional email
        html_content = create_professional_email_template(ticket)
        
        message = Mail(
            from_email='adrianaanuar1241@gmail.com',
            to_emails=ticket["email"],
            subject=f'QuickAid Ticket Submitted - {ticket["title"]}',
            html_content=html_content
        )
        
        # Send email and log result
        email_response = sg.send(message)
        logging.info(f"Email sent for ticket {ticket['id']}, status: {email_response.status_code}")

        # Return success response
        return func.HttpResponse(
            json.dumps({
                "message": "Ticket submitted successfully", 
                "id": ticket["id"],
                "status": ticket["status"],
                "email_sent": email_response.status_code == 202,
                "created_at": ticket["created_at"]
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in submit_ticket: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to submit ticket", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
