# Project Plan: OpenRedact (Open Source Data Removal Agent)

## 1. Project Overview
**Goal:** Create an open-source, self-hosted alternative to Incogni for automated personal data removal from data brokers.
**Core Philosophy:** Privacy-first, transparent, modular, and agent-ready (MCP & OpenClaw native).

## 2. Architecture Options

### Option A: Standalone Local Tool (CLI + Skill)
*   **Structure:** Python scripts running locally.
*   **Pros:** Maximum privacy (data never leaves your machine), free.
*   **Cons:** Must keep computer on for long-running scraping tasks; IP reputation issues (scraping from residential IP is good, but heavy volume might get flagged).

### Option B: Cloud Native Agent (Recommended)
*   **Structure:** Serverless Container (Google Cloud Run / AWS Lambda) exposing an MCP Server.
*   **Pros:** 24/7 operation, scalable, clean abstraction.
*   **Cons:** Requires cloud setup (free tier feasible).

## 3. Proposed Architecture (Hybrid)

We will build **OpenRedact** as a modular Python application that can run in both modes.

### Core Components

1.  **`core/` (The Brain)**
    *   **`BrokersRegistry`**: A plugin system for data brokers.
    *   **Scrapers**: Playwright/BeautifulSoup implementations for specific sites (e.g., Whitepages, Spokeo).
    *   **`WorkflowEngine`**: State machine to handle "Submit Request" -> "Wait for Email" -> "Confirm" loops.
    *   **`IdentityManager`**: Encrypted local storage of PII (User profile).

2.  **`interfaces/`**
    *   **`mcp_server.py`**: Exposes the core logic as Model Context Protocol tools (`list_brokers`, `start_removal`, `get_status`).
    *   **`cli.py`**: Standard terminal interface.

3.  **`integrations/`**
    *   **OpenClaw Skill**: A `SKILL.md` definition that points OpenClaw to the local or remote MCP server.

## 4. Technology Stack
*   **Language:** Python 3.11+ (Best for scraping/automation).
*   **Scraping:** Playwright (headless browser) + `requests`.
*   **Database:** SQLite (local) / PostgreSQL (cloud).
*   **Queues:** Redis (optional, for heavy background jobs) or simple in-memory for MVP.
*   **API/MCP:** FastMCP or bespoke FastAPI implementation.

## 5. Development Phases

### Phase 1: MVP (Local)
*   Define the `Broker` abstract base class.
*   Implement 1 "easy" broker (e.g., a simple opt-out form).
*   Create a CLI to trigger the removal.
*   **Deliverable:** A script that takes user details and submits one form.

### Phase 2: Agentification (MCP & OpenClaw)
*   Wrap the CLI tools in an MCP server.
*   Create `SKILL.md` for OpenClaw.
*   **Deliverable:** You can ask OpenClaw "Remove me from Broker X" and it executes.

### Phase 3: Cloud & Scale
*   Dockerize the application.
*   Add "Push" notifications (email/webhook) when a removal is confirmed.
*   Deploy to AWS/GCP Free Tier.

## 6. Next Steps
1.  Initialize the Python project structure.
2.  Define the `UserSchema` (what data do we need? Name, address, email, phone).
3.  Select the first 3 target data brokers (e.g., generic people search engines).

## Questions for You
1.  **Cloud Provider:** Do you prefer AWS (Lambda/Fargate) or GCP (Cloud Run)? Cloud Run is often easier for containerized scraping.
2.  **Persistence:** Is SQLite (file-based) sufficient for the start, or should we plan for Postgres?
