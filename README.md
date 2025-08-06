# QuickAid – Smart Campus Helpdesk

Beginner-friendly Azure-based helpdesk app using:
- Static HTML frontend
- Python Azure Functions backend
- Cosmos DB for data storage

## Deployment

### 1. Frontend
Deploy `frontend/index.html` to Azure App Service.

### 2. Backend
Deploy `api/` using VS Code Azure Functions extension.

### 3. Cosmos DB
Create:
- Database: `QuickAidDB`
- Container: `Tickets` with partition key `/id`
Add `COSMOS_ENDPOINT` and `COSMOS_KEY` to Azure Function App settings.
