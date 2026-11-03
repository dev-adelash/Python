# Financial Reconciliation and Exception Workbench

Built a FastAPI and SQLite application service for signed payment callbacks and integer-cent reconciliation. Routed partial matches to reviewer proposals with explicit approval and audit records. Tested duplicate callbacks, signature failures and conflicting approvals with pytest using synthetic invoices.

## Run locally

Start from the `python/` directory of this repository.

```sh
python run.py financial-reconciliation-and-exception-workbench-python --port 8000
```

The browser console is available at `http://127.0.0.1:8000` for API applications. For frontend applications, use the frontend development server described in the setup below.

## Architecture

```mermaid
flowchart LR
    Client[Browser or API client] --> API[Validated API]
    API --> Rules[Business rules]
    Rules --> State[Application state]
    Rules --> Audit[Audit history]
```

## Workflow

Available actions: `callback`, `propose`, `approve`.

Open `project.json` for the available commands and example inputs when present. Use the operator role to inspect state and audit history. Retry an accepted command with the same identifier to observe replay behavior; change its payload or expected version to exercise conflict handling.

## Verification

Run the automated checks from the stack directory:

```sh
python -m pytest -q
```

The checks exercise business rules, permission boundaries and failure recovery. Sample records are synthetic. Development credentials are local examples; use managed identity, external secrets and your own deployment controls before exposing services publicly.

## Implementation notes

# Financial Reconciliation and Exception Workbench

Validate callback signatures and event IDs, match exact integer-cent balances and retain exceptions. Reviewer proposals require explicit approval and cannot overdraw a changed balance.

## Purpose

Validate callback signatures and event IDs, match exact integer-cent balances and retain exceptions. Reviewer proposals require explicit approval and cannot overdraw a changed balance.

## Run

See the family-level README one directory above for the installed runtime and command. Use this folder's `project.json` to select this application.

## Workflow

Domain: **finance**. Available commands: callback, propose, approve.

The configuration includes request examples. Inspect state and the audit log after a successful command, then retry it or change its version to observe duplicate and concurrency behavior.

## Configuration

Core workflow demo only. Local fixture authentication and local development storage. External cloud services, live AI model calls and production database/broker integrations from the broader CV descriptions are not configured here. Read the family-level README for the actual implemented stack and tests.

## Architecture

[Architecture and failure boundaries](ARCHITECTURE.md). Shared workflow modules and tests are in the parent stack folder.

