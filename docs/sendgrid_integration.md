# ✉️ Integrate SendGrid for Email Notifications

## Purpose:
Send an email confirmation when a helpdesk ticket is submitted.

## Setup:
1. Sign up at https://sendgrid.com/ and get a free API key.
2. In Azure:
   - Add the API key to your Function App settings: `SENDGRID_API_KEY`
3. In `submit_ticket`, send email after saving to Cosmos DB.

## Python Example:
```python
import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key=os.environ['SENDGRID_API_KEY'])
message = Mail(
    from_email='support@example.com',
    to_emails=data["email"],
    subject='QuickAid Ticket Submitted',
    html_content='Your ticket has been received.'
)
sg.send(message)
```

## Note:
SendGrid free tier allows 100 emails/day.
