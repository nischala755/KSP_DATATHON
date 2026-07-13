# Zoho Catalyst AppSail deployment runbook

This runbook follows the current official Catalyst deployment model. AppSail supports Python managed runtimes and OCI-compatible Linux AMD64 containers. PRAHARI uses the container path so the compiled React client and FastAPI server share one origin and one qualifying URL.

Official references:

- AppSail overview: `https://docs.catalyst.zoho.com/en/serverless/help/appsail/introduction/`
- Custom-runtime CLI deployment: `https://docs.catalyst.zoho.com/en/serverless/help/appsail/custom-runtimes/deploy-from-cli/`
- AppSail configuration and port: `https://docs.catalyst.zoho.com/en/serverless/help/appsail/appsail-configurations/`
- CLI quick start: `https://docs.catalyst.zoho.com/en/getting-started/quick-start-guide/`
- Deploy resources: `https://docs.catalyst.zoho.com/en/cli/v1/deploy-resources/introduction/`

## What has already been prepared

- `Dockerfile.catalyst` builds the frontend, installs the API and runs Uvicorn.
- The application serves `frontend_dist` as an SPA after registering all API routes.
- The frontend uses same-origin API URLs in production.
- `.dockerignore` excludes secrets, caches, databases, presentations and local build output.
- The server listens on `X_ZOHO_CATALYST_LISTEN_PORT`, defaulting to 9000 locally.
- The AppSail image intentionally omits a numeric OCI `USER`; Catalyst's bundle creator rejects numeric user IDs and applies its runtime isolation itself.

## Confirmed datathon project

| Field | Value |
|---|---|
| Data center | India (`in`) |
| Organization ID | `60077990572` |
| Project ID | `51972000000013024` |
| Current environment | Development |
| Console route | `https://console.catalyst.zoho.in/baas/60077990572/project/51972000000013024/Development#/slate` |
| AppSail service ID | `51972000000017001` |
| Verified Development URL | `https://prahari-50043921178.development.catalystappsail.in` |

The console route is private administration UI and must not be submitted as the deployed solution link. The submission link must be the public AppSail endpoint created after deployment and production promotion.

## Verified deployment record — 13 July 2026

The `prahari` custom-runtime service is deployed and active in Development. Public verification returned:

| Check | Result |
|---|---|
| React homepage | HTTP 200 |
| FastAPI documentation | HTTP 200 |
| Health | `status=ok`, `cases=500` |
| Grounded Mysuru IPC 420 query | 9 matching records, high confidence |
| Returned citation objects | 8 |
| Audit chain | 1 entry, verified |

The first OCI deployment failed because Catalyst's bundle creator rejected `USER 10001` with `Invalid user id in config: 10001`. The corrected image omits the numeric OCI `USER`, relies on Catalyst runtime isolation, and deployed successfully from a pure OCI archive.

## Step 1 — Create or open the qualifying Catalyst project

1. Open `https://catalyst.zoho.com/promotions.html?cn=KSPH26`.
2. Sign in with the team's Zoho account.
3. Create or select the project registered for the KSP Datathon promotion.
4. Note the project name, project ID, organization and India data center.

The first Catalyst project must be created through the web console. Do not create an unrelated non-promotional project if the evaluation requires the promotion-linked workspace.

## Step 2 — Install and authenticate the CLI

```powershell
cmd /c npm install -g zcatalyst-cli
cmd /c catalyst --version
cmd /c catalyst login --dc in
cmd /c catalyst whoami --dc in
```

`catalyst login` opens an interactive Zoho authorization page. Complete this yourself. Never send your Zoho password, session cookie or one-time password to a teammate or assistant.

## Step 3 — Build and test the AppSail image

Catalyst custom-runtime images must be OCI-compatible Linux AMD64 images.

```powershell
docker build --platform linux/amd64 -f Dockerfile.catalyst -t prahari-catalyst:latest .
docker run --rm -p 9000:9000 `
  -e X_ZOHO_CATALYST_LISTEN_PORT=9000 `
  -e JWT_SECRET=local-smoke-test-secret `
  -e AUDIT_SIGNING_KEY=local-smoke-test-audit-key `
  prahari-catalyst:latest
```

In another terminal:

```powershell
Invoke-RestMethod http://localhost:9000/api/health
```

Expected result includes `status: ok` and `cases: 500`.

## Step 4 — Initialize the Catalyst project directory

From the repository root:

```powershell
cmd /c catalyst init --dc in
```

When prompted:

1. Select the datathon organization.
2. Select the existing KSP Datathon Catalyst project.
3. Select **AppSail**.
4. Choose **Docker Image** / custom runtime.
5. Choose the local Docker image protocol.
6. Select `prahari-catalyst:latest`.
7. Name the service `prahari`.

Catalyst writes the actual project association into `catalyst.json`. Do not fabricate project IDs manually.

## Step 5 — Configure server-side environment variables

In the Catalyst console, open **Serverless > AppSail > prahari > Configuration** and configure:

```text
LLM_PROVIDER=mock
JWT_SECRET=<new-long-random-value>
AUDIT_SIGNING_KEY=<different-new-long-random-value>
DATABASE_URL=sqlite:////app/data/prahari.db
CORS_ORIGINS=<generated-appsail-origin>
```

For remote intent parsing, add only one freshly rotated provider key and switch `LLM_PROVIDER` accordingly:

```text
LLM_PROVIDER=mistral
MISTRAL_API_KEY=<fresh-server-side-key>
```

or:

```text
LLM_PROVIDER=sarvam
SARVAM_API_KEY=<fresh-server-side-key>
```

Do not reuse the keys previously pasted into chat. Do not put provider keys in `VITE_*` variables because Vite embeds them in browser JavaScript.

## Step 6 — Deploy to the development environment

After initialization:

```powershell
cmd /c catalyst deploy appsail --dc in
```

The CLI displays the AppSail endpoint after deployment. Save it in a secure team note and test:

```text
https://<generated-appsail-host>/
https://<generated-appsail-host>/api/health
https://<generated-appsail-host>/docs
```

The CLI deploys resources to Catalyst's development environment. This development endpoint is not automatically the production deployment.

## Step 7 — Validate the live service

Run all of these before promotion:

1. Load the homepage in an incognito browser.
2. Confirm `/api/health` returns 500 cases.
3. Ask the Mysuru IPC 420 question.
4. Ask the Kannada demonstration question.
5. Open FIR citation chips.
6. Open **Explain this answer** and verify the chain.
7. Open Operations Overview.
8. Review AppSail execution logs for startup or file-permission errors.
9. Confirm no secret appears in browser developer tools or the JS bundle.

## Step 8 — Promote to production

Official Catalyst documentation states that CLI deployments update the development environment. To make the app available in production, use the Catalyst web console:

1. Switch to the production environment in the console.
2. Review billing/payment requirements for production activation.
3. Promote or deploy the tested AppSail version to production.
4. Recreate the required environment variables in production; development variables may not automatically apply.
5. Open the production URL in an incognito browser.
6. Repeat the complete live-service validation.

Use the final production Catalyst URL as the **Deployed Solution Link** in the datathon portal and slide 13.

## Step 9 — Record deployment evidence

Capture:

- AppSail service name and healthy status
- Deployment timestamp and version
- Production URL
- `/api/health` response
- One grounded chat response
- One verified audit-chain response

Never capture environment-variable values.

## Known prototype persistence limitation

SQLite resides inside the AppSail runtime filesystem. It is suitable for the seeded demonstration because the database can be recreated, but runtime-local writes should not be treated as durable production persistence across instance replacement or scaling.

For production, migrate FIR, user and audit tables to a durable managed service before relying on post-startup writes. Retain the fixed synthetic seeding path only for demonstrations.

## Rollback

If the new deployment fails:

1. Inspect AppSail execution logs.
2. Confirm the service listens on `X_ZOHO_CATALYST_LISTEN_PORT` and `0.0.0.0`.
3. Confirm the image is Linux AMD64.
4. Confirm required environment variables are present.
5. Restore the last healthy AppSail deployment from the console.
6. Do not delete a production project merely to fix a release.
