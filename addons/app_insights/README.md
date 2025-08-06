# 📊 Adding Application Insights to Azure Function

## Purpose:
Track usage, performance, and errors.

## Steps:
1. Enable "Application Insights" when creating the Function App.
2. Inside your Python function:
```python
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing request for submit_ticket")
    ...
```
3. Go to Application Insights > Logs to view telemetry.

## Bonus:
Use `track_event`, `track_exception`, etc., with the Application Insights SDK.
