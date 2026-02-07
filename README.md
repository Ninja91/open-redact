# OpenRedact

An open-source, self-hosted personal data removal agent.

## GCP Setup & CI/CD

### 1. GitHub Secrets
To enable automated deployment to Cloud Run, go to your GitHub Repository Settings > Secrets and variables > Actions and add the following:

- `GCP_SA_KEY`: The **JSON content** of the service account key for `mainRedactor@open-redact-486721.iam.gserviceaccount.com`.
- `DATABASE_URL`: Your PostgreSQL connection string (e.g., `postgresql://user:password@host:5432/dbname`).

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
Point your OpenClaw or Gemini CLI to the following endpoint once deployed:
`https://open-redact-xxxx.a.run.app/mcp/sse`

## Project Structure
- `src/brokers/`: Scraper implementations for data brokers.
- `src/models/`: Database schema and ORM.
- `src/api/`: FastAPI & MCP tool definitions.
- `SKILL.md`: OpenClaw skill definition.
