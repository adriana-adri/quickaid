import azure.functions as func
import logging
import json
import uuid
import os
from datetime import datetime
from azure.cosmos import CosmosClient
import sendgrid
from sendgrid.helpers.mail import Mail
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize Azure Function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Configure Key Vault connection
vault_url = "https://quickaid.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve secrets from Key Vault
COSMOS_ENDPOINT = client.get_secret("CosmosEndpoint").value
COSMOS_KEY = client.get_secret("CosmosKey").value
SENDGRID_API_KEY = client.get_secret("SendGridApiKey").value

def create_professional_email_template(ticket_data):
    """Create a professional HTML email template for ticket confirmation"""
    try:
        # Use the same email template as in index.html
        html_template = '''
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
                            <td style="padding: 8px 0; color: #333;">{{TICKET_ID}}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; color: #555;">Title:</td>
                            <td style="padding: 8px 0; color: #333;">{{TITLE}}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; color: #555;">Category:</td>
                            <td style="padding: 8px 0; color: #333;">{{CATEGORY}}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; color: #555;">Status:</td>
                            <td style="padding: 8px 0;">
                                <span style="background-color: #e74c3c; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                                    {{STATUS}}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; color: #555;">Submitted:</td>
                            <td style="padding: 8px 0; color: #333;">{{TIMESTAMP}}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #856404;">📋 Issue Description:</h4>
                    <p style="margin: 0; color: #856404; font-style: italic;">"{{DESCRIPTION}}"</p>
                </div>
                
                <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #0c5460;">⏱️ What happens next?</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #0c5460;">
                        <li>Our support team will review your ticket within 2 hours</li>
                        <li>You'll receive updates via email at: <strong>{{EMAIL}}</strong></li>
                        <li>Expected resolution time: 24-48 hours for {{CATEGORY}} issues</li>
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
        
        # Replace placeholders with actual data
        html_content = html_template.replace('{{TICKET_ID}}', ticket_data["id"])
        html_content = html_content.replace('{{TITLE}}', ticket_data["title"])
        html_content = html_content.replace('{{CATEGORY}}', ticket_data["category"])
        html_content = html_content.replace('{{STATUS}}', ticket_data["status"])
        html_content = html_content.replace('{{DESCRIPTION}}', ticket_data["description"])
        html_content = html_content.replace('{{EMAIL}}', ticket_data["email"])
        html_content = html_content.replace('{{TIMESTAMP}}', datetime.now().strftime("%B %d, %Y at %I:%M %p"))
        
        return html_content
        
    except Exception as e:
        logging.error(f"Error creating email template: {str(e)}")
        # Fallback to a simple HTML template
        return f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">QuickAid Ticket Confirmation</h2>
            <p>Your ticket <strong>{ticket_data["id"]}</strong> has been submitted successfully.</p>
            <p><strong>Title:</strong> {ticket_data["title"]}</p>
            <p><strong>Category:</strong> {ticket_data["category"]}</p>
            <p><strong>Status:</strong> {ticket_data["status"]}</p>
            <p><strong>Description:</strong> {ticket_data["description"]}</p>
            <p>Thank you for using QuickAid Helpdesk!</p>
        </div>
        '''

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

@app.route(route="submit_ticket", methods=["POST"])
def submit_ticket(req: func.HttpRequest) -> func.HttpResponse:
    """
    Submit a support ticket with professional email notification
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
        cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        db = cosmos_client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")
        container.create_item(body=ticket)
        
        logging.info(f"Ticket {ticket['id']} saved to Cosmos DB successfully")

        # Send confirmation email with SendGrid
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
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
