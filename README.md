# OpenRedact

An open-source, self-hosted personal data removal agent. OpenRedact helps you automate the process of requesting data deletion from various data brokers.

## Features
- **Modular Scrapers**: Support for CyberBackgroundChecks, OfficialUSA, and TruePeopleSearch.
- **MCP Native**: Exposes a Model Context Protocol server for seamless integration with AI agents.
- **Privacy First**: Self-hosted on your own GCP account with your own database.

## GCP Setup & CI/CD (BYOK Model)

To deploy your own instance:

### 1. GitHub Secrets
Add the following secrets to your GitHub Repository:
- `GCP_PROJECT_ID`: Your Google Cloud Project ID.
- `GCP_SA_KEY`: JSON content of a Service Account key (Cloud Run Admin, Storage Admin).
- `DATABASE_URL`: Your PostgreSQL connection string (e.g., Neon.tech).

### 2. Deployment
Pushing to the `master` branch will automatically deploy the service to Google Cloud Run. Once deployed, note your service URL (e.g., `https://open-redact-xyz.a.run.app`).

## Using with OpenClaw

OpenRedact is designed to be used as an **OpenClaw Skill**.

### 1. Configure the Skill
Add the OpenRedact skill to your OpenClaw configuration. You can point it directly to your deployed MCP endpoint:

```yaml
# In your OpenClaw skills configuration
- name: OpenRedact
  url: https://<your-cloud-run-url>/mcp/sse
```

### 2. Available Tools
Once integrated, you can use the following commands through your agent:

*   **`list-brokers`**: See which brokers are currently supported.
*   **`register-me`**: Provide your identity details (Name, Email, City, State) so the agent knows what to look for.
*   **`remove-me`**: Trigger the removal process for a specific broker.

### 3. Example Interaction
> **User**: "Register me as John Doe, john.doe@email.com, living in Seattle, WA."
> **Agent**: "User John Doe registered successfully."
>
> **User**: "Remove my data from TruePeopleSearch."
> **Agent**: "Status: pending. Message: Removal request sent. Verification email should follow."

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the DB initialization
python -m src.models.init_db

# Start the server
uvicorn src.api.main:app --reload
```

## Supported Brokers
- CyberBackgroundChecks
- OfficialUSA
- TruePeopleSearch
- ExampleDataBroker (for testing)
