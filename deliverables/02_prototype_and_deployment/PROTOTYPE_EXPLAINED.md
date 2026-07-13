# PRAHARI explained from first principles

## The idea in one sentence

PRAHARI is a bilingual investigation-support platform that lets authorized officers ask questions about FIR data, discover explainable cross-station patterns, and verify the evidence and audit history behind every answer.

## The operational problem

Investigators often need to connect incidents that were filed in different places, described with different words, or recorded in different languages. A distinctive burglary method may appear at several stations, but the relationship is not obvious when records are reviewed one station at a time. Traditional exact-keyword search can also miss two narratives that describe the same method using different wording.

A generic LLM interface creates a different problem: it may answer fluently without an enforceable connection to source records. In a high-accountability setting, a plausible sentence is not enough. The operator needs to know:

- Which records were actually searched?
- Why were these cases considered related?
- Was the officer authorized to see them?
- Did the answer cite a record that does not exist?
- Can the interaction be reconstructed later?

PRAHARI makes these questions part of the architecture rather than leaving them to prompt wording.

## The core design decision

The language model never writes or executes SQL or Cypher.

Instead, a question becomes a small, validated intent:

```json
{
  "entity_type": "case",
  "filters": {
    "district": "Mysuru",
    "ipc_section": "420"
  },
  "requested_action": "aggregate",
  "language": "en"
}
```

Trusted application code maps this intent to SQLAlchemy expressions with bound parameters. The authenticated user's station or district is added separately. Even if a prompt asks the model to “ignore jurisdiction” or “drop the users table,” there is no field in the schema that can express those commands.

## A complete request lifecycle

### 1. The officer asks a question

The chat endpoint receives a message and conversation ID. The request may optionally include a preferred language.

### 2. PRAHARI detects language

Kannada Unicode ranges trigger Kannada mode. A narrow list of common Kanglish cues selects Kanglish mode. Everything else uses English.

### 3. A provider parses intent

The selected provider is one of:

- Mistral API adapter
- Sarvam AI adapter
- Deterministic local parser

Remote providers receive a strict “JSON only, never SQL/Cypher” instruction. Their response must validate as the Intent model. Any timeout, API error, malformed JSON or invalid schema falls back to the local parser.

### 4. The trusted query builder adds authority

The application builds the database query from allow-listed filters. It then applies:

- Station ID for a constable or SHO
- District for a district SP
- Statewide access for SCRB admin

This is more reliable than asking the model to remember a user's permissions.

### 5. Records are retrieved

Only application-created parameterized queries reach the database. The response context contains the actual FIR records that matched.

### 6. An evidence-bound answer is generated

The local renderer uses only retrieved rows. If no row matches, it responds that the information is unavailable. It never fills a gap by inference.

### 7. Citations are checked

The API extracts every bracketed FIR ID from the answer. If any ID is outside the retrieved allow-list, the response is rejected with a grounding error rather than returned to the officer.

### 8. The turn is audited

The question, intent, retrieved IDs, answer, user and previous hash become a canonical payload. PRAHARI hashes and signs it, then appends it to the conversation chain.

## What the prototype demonstrates

### Bilingual chat

Officers can query in English or Kannada. The local parser supports a narrow, reliable vocabulary for the offline demo. Mistral or Sarvam can broaden language coverage when a fresh server-side key is configured.

### Grounded citations

Answers expose FIR IDs as source chips. A citation is not merely generated text: the backend checks it against retrieval results.

### Explainable modus-operandi similarity

Each synthetic FIR has structured MO elements. A source case may include:

```text
rear-window entry
night-time
jewellery targeted
```

PRAHARI searches different stations, calculates overlap, applies a synthetic-cluster bonus for demonstration data, and returns both a score and the shared elements. The investigator sees why two cases were surfaced.

### Role and jurisdiction scope

Four seeded roles demonstrate the authority hierarchy. The rule exists in server-side retrieval code rather than being a visual-only restriction.

### Explainable audit trail

The UI's “Explain this answer” action retrieves the conversation chain and shows whether every link and signature verifies.

### Area-level dashboard

The dashboard intentionally displays aggregates rather than individual risk scores. It helps operators understand case distribution without converting historical records into an unreviewed prediction about a person.

### Confirmation-first ingestion

The scanned-FIR endpoint accepts a document and returns a confirmation-required response. OCR/VLM extraction remains a clearly labeled adapter. The prototype never silently writes model-extracted fields into the case database.

## Synthetic dataset

The seed process creates 500 fictional FIRs across 15 Karnataka districts and 18 repeated MO patterns. It uses a fixed random seed so demonstrations and tests are reproducible.

The dataset includes:

- FIR ID and number
- Filing station and district
- Incident date
- IPC section list
- English and Kannada synthetic narrative
- Synthetic coordinates
- Case status and outcome
- Fictional people and roles
- Vehicle and weapon fields
- MO cluster and structured elements

No real police data, real person or real incident is represented. The deliberate clusters are test fixtures, not a crime model.

## Important implementation boundaries

### Fully working

- FastAPI application and documented endpoints
- React/TypeScript operator interface
- 500-record deterministic seed
- Intent validation and trusted retrieval
- English/Kannada narrow parsing
- Mistral/Sarvam provider switch and local fallback
- Citation allow-list
- Cross-station structured MO matching
- JWT demo identities and query-layer scope
- Hash-chain audit and HMAC signature fallback
- Dashboard and fairness note
- AppSail-compatible single-origin container
- Automated backend tests and frontend build

### Production-shaped but scoped

- Live PostgreSQL/pgvector migration
- Live Neo4j dual-write and graph UI
- ML-DSA signatures
- IndicTrans2 and Bhashini adapters
- Production OCR/Pixtral extraction
- Enterprise SSO
- Hotspot map rendering
- Real-data accuracy and threshold calibration

This separation should remain visible in every pitch. Honest scoping increases credibility and prevents accidental claims about capabilities that are not yet evaluated.

## Why this is responsible AI

PRAHARI does not claim that technical grounding makes an answer legally or operationally correct. Grounding establishes provenance, not truth. A retrieved FIR may contain errors, historical bias or incomplete facts.

The responsible design therefore includes:

- Human review of every operational conclusion
- No individual propensity or risk score
- Explicit retrieval and citation boundaries
- Jurisdiction-aware access
- Confirmation before document persistence
- Audit reconstruction
- Honest synthetic-data labeling
- Abstention when evidence is absent

## How Catalyst fits

The qualifying deployment uses Catalyst AppSail to host one container containing:

- The compiled React frontend
- The FastAPI backend
- The synthetic demo database created on first startup

Serving frontend and API from one origin avoids CORS configuration and produces one live link for the submission. AppSail supplies the listen port through `X_ZOHO_CATALYST_LISTEN_PORT`, which the container startup command passes to Uvicorn.

The next production migration would replace demo persistence with managed Catalyst services and add mandatory Catalyst authentication.

## The strongest pitch sentence

**PRAHARI does not ask police to trust an AI answer; it gives them a controlled path from question to evidence, with jurisdiction, explanation and audit at every step.**

