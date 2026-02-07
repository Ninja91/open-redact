---
name: OpenRedact
description: An open-source personal data removal agent.
metadata: {"version": "0.1.0", "author": "OpenRedact Team"}
commands:
  - name: list-brokers
    description: List all supported data brokers.
    dispatch: tool
    tool: list_supported_brokers
  - name: register-me
    description: Register your identity for data removal.
    dispatch: tool
    tool: register_user
  - name: remove-me
    description: Start the removal process from a broker.
    dispatch: tool
    tool: start_removal
---

# OpenRedact Skill

This skill allows you to manage your personal data removal from data brokers directly through OpenClaw.

## Setup
1. Deploy the OpenRedact server (Cloud Run or Local).
2. Point your OpenClaw environment to the MCP endpoint.

## Usage
- "What brokers do you support?"
- "Register me as [Name] with email [Email]."
- "Remove my data from ExampleDataBroker."
