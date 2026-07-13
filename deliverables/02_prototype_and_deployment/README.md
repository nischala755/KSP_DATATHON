# PRAHARI prototype and deployment handbook

This folder explains the product from first principles and provides the Catalyst deployment runbook.

## Reading order

1. `PROTOTYPE_EXPLAINED.md` — what the idea is, why it matters and how every component works.
2. `DEMO_AND_QA_GUIDE.md` — three-minute demo script and judge-question answers.
3. `CATALYST_DEPLOYMENT_RUNBOOK.md` — exact deployment and production-promotion steps.
4. `SUBMISSION_CHECKLIST.md` — final evidence and link checklist.

## Current deployment state

- Application code: AppSail-compatible
- Single-origin React + FastAPI container: implemented in `Dockerfile.catalyst`
- Catalyst CLI: must be installed and authenticated
- Catalyst project association: requires a teammate's Catalyst account
- Live solution URL: pending deployment

The live URL cannot be created without an authenticated Catalyst project. Never share a Zoho password or browser session; complete `catalyst login` interactively.

