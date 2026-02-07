# OpenRedact

An open-source, self-hosted personal data removal agent. OpenRedact helps you automate the process of requesting data deletion from various data brokers.

## GCP Setup & CI/CD (BYOK Model)

To deploy your own instance of OpenRedact to Google Cloud Run:

### 1. GitHub Secrets
Add the following secrets to your GitHub Repository (Settings > Secrets and variables > Actions):

- `GCP_PROJECT_ID`: Your Google Cloud Project ID.
- `GCP_SA_KEY`: The **JSON content** of a Service Account key with `Cloud Run Admin` and `Storage Admin` (for GCR) permissions.
- `DATABASE_URL`: Your PostgreSQL connection string (e.g., from Neon.tech or Supabase).

### 2. Local Development
```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the DB initialization
python -m src.models.init_db

# Start the server
uvicorn src.api.main:app --reload
```

### 3. MCP Integration (OpenClaw)
Once deployed, point your OpenClaw or Gemini CLI to the following endpoint:
`https://<your-cloud-run-url>/mcp/sse`
