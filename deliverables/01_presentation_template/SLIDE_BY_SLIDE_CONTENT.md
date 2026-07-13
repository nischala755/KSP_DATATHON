# PRAHARI — complete slide-by-slide content

Every slide below includes copy, visual direction, speaker guidance, and evidence boundaries. Replace all `{TEAM INPUT}` fields before submission.

## Slide 1 — Team Details

### Headline

**PRAHARI — Grounded Crime Intelligence for Karnataka Police**

### Template fields

- Team name: `{TEAM INPUT}`
- Team leader: `{TEAM INPUT}`
- Team size: `{TEAM INPUT}`
- Team members: `{TEAM INPUT — names and roles}`
- Problem statement: **Bilingual, evidence-grounded discovery of cross-station crime patterns from fragmented FIR data**

### One-line positioning

**Ask in English or Kannada. Retrieve verified FIR evidence. Discover explainable links. Audit every answer.**

### Visual

Use four small chips at the bottom: `Bilingual`, `Cited`, `Explainable`, `Auditable`.

### Speaker note

“PRAHARI is not a generic chatbot and not predictive policing. It is a controlled investigation-support layer that helps an officer retrieve and connect existing records, with provenance for every answer.”

## Slide 2 — Brief about the solution

### Headline

**From a question to evidence in seconds**

### Problem

Crime patterns cross station boundaries, languages and data silos. Manual discovery is slow, keyword search misses narrative similarity, and unrestricted generative AI can produce answers that are difficult to verify.

### Solution

PRAHARI converts an officer's English/Kannada question into a constrained intent, applies role-scoped deterministic retrieval, returns cited FIR records, highlights shared MO elements across stations, and writes a signed audit entry.

### Proof cards

- **500** synthetic FIRs
- **15** Karnataka districts
- **18** deliberately repeated MO clusters
- **4** jurisdiction-aware roles

### Visual

Insert `visuals/04_scale_and_scope.svg` or use the four proof cards beside a product screenshot.

### Speaker note

“We deliberately built a repeatable synthetic dataset because real SCRB data is not available. The value of the prototype is the safe investigation workflow, not a fabricated real-world accuracy claim.”

## Slide 3 — Opportunity, differentiation and USP

### Headline

**The intelligence is useful because it is constrained**

### Three-column comparison

| Conventional search | Generic GenAI assistant | PRAHARI |
|---|---|---|
| Exact keywords | Flexible language | Flexible language + controlled intent |
| Station-by-station | Can synthesize broadly | Cross-station retrieval |
| No narrative similarity | May hallucinate | Retrieved-ID citation guard |
| Limited explanation | Opaque model output | Shared MO elements |
| Basic logs | Prompt history | Signed hash-chain audit |
| Manual data scope | Scope can be prompted around | Jurisdiction enforced in code |

### USP statement

**PRAHARI is an evidence-bound conversational layer: the LLM can classify the question, but it cannot write a database query or cite a record that was not retrieved.**

### Opportunity

- Faster cross-jurisdiction pattern discovery
- Kannada-first accessibility for field users
- Explainable collaboration between station, district and state levels
- Auditable AI adoption for high-accountability workflows

### Speaker note

Focus on the architectural boundary. Do not say “zero hallucinations.” Say “unknown FIR citations are programmatically rejected, and empty retrievals trigger abstention.”

## Slide 4 — Features

### Headline

**Six capabilities, one investigation workspace**

### Feature cards

1. **Bilingual intelligence chat** — English, Kannada and narrow Kanglish handling.
2. **Grounded FIR answers** — confidence labels and expandable record citations.
3. **Cross-station MO links** — ranked cases with specific shared methods.
4. **Jurisdiction-aware RBAC** — constable, SHO, district SP and SCRB admin.
5. **Explain this answer** — query, intent, retrieved IDs and signature verification.
6. **Responsible dashboard** — area aggregates only; no individual risk scoring.

### Footer

**Human-confirmation scanned-FIR ingestion is included as a scoped demo path.**

### Visual

Use six dark cards in a 3 x 2 grid. Assign teal to chat/citations, blue to links/RBAC and violet to audit/dashboard.

## Slide 5 — Process flow

### Headline

**Six trust gates between the officer and the answer**

### Visual

Use `visuals/01_grounded_pipeline.svg` full-width.

### Supporting labels

`Question -> Validated Intent -> Role Scope -> Parameterized Retrieval -> Citation Check -> Signed Audit`

### Speaker note

“The LLM never receives authority to query the database. Its output is validated as a small Pydantic object. User jurisdiction is added independently. The final answer is checked against the retrieved FIR ID allow-list before it is returned.”

## Slide 6 — Wireframes and use cases

### Headline

**Designed around three operator moments**

### Panel A — Ask

- Query: “How many IPC 420 cases are in Mysuru?”
- Response: aggregate answer, confidence and FIR citations
- Action: open a cited source record

### Panel B — Connect

- Select an FIR
- Review cross-station similar cases
- See exact shared MO elements rather than only a score

### Panel C — Explain

- Open “Explain this answer”
- Inspect parsed intent and retrieved IDs
- Verify the signed audit chain

### Visual

Use three equal-width cropped product screenshots with captions `ASK`, `CONNECT`, `VERIFY`.

### Speaker note

Keep this slide user-centered. Technical architecture belongs on slide 7.

## Slide 7 — Architecture

### Headline

**Separation of language, authority, retrieval and evidence**

### Visual

Use `visuals/02_architecture.svg` full-width.

### Architecture callouts

- React operator workspace
- FastAPI trusted intelligence layer
- Mistral/Sarvam interchangeable intent provider
- SQLAlchemy relational retrieval
- Explainable MO scorer
- JWT jurisdiction enforcement
- Hash-chain audit service
- Zoho Catalyst AppSail deployment

### Speaker note

Clearly distinguish the working SQLite demo from the production target of PostgreSQL/pgvector and Neo4j. The diagram labels those boundaries explicitly.

## Slide 8 — Technologies

### Headline

**Open, modular and production-shaped**

### Technology matrix

| Layer | Technology | Purpose |
|---|---|---|
| Experience | React, TypeScript, Vite | Responsive operator interface |
| API | Python, FastAPI, Pydantic | Typed requests and orchestration |
| Retrieval | SQLAlchemy | Bound, deterministic database queries |
| Demo store | SQLite | Zero-infrastructure judging path |
| Production data | PostgreSQL + pgvector | FIR source and embedding candidates |
| Relationship graph | Neo4j | Person, case, vehicle and MO links |
| Language AI | Mistral + Sarvam adapters | Constrained intent classification |
| Security | JWT, SHA-256, HMAC | RBAC and audit integrity |
| Cloud | Zoho Catalyst AppSail | Mandatory live hosting |
| Quality | Pytest, TypeScript compiler | Reproducible verification |

### Speaker note

Avoid showing logo soup. Group technologies by the trust boundary they serve.

## Slide 9 — Catalyst services

### Headline

**Catalyst-native deployment with a clear migration path**

### Used for the submitted prototype

**AppSail**

- Hosts the combined FastAPI API and compiled React application
- Uses the Catalyst-provided listen port
- Provides the qualifying live deployment URL
- Supports environment variables for server-side provider credentials

### Next Catalyst services

- **Data Store:** replace the ephemeral/demo SQLite source for managed persistent records
- **Authentication:** replace seeded JWT users with managed officer identity
- **API Gateway:** centralize policies, throttling and API observability
- **Stratus:** retain approved scanned-FIR objects
- **Cache:** accelerate safe aggregate queries
- **Pipelines:** automate tested deployments from `main`

### Important accuracy label

Use two headings: `ACTIVE IN SUBMISSION` and `PRODUCTION MIGRATION`, so planned services are not misrepresented as already integrated.

## Slide 10 — Estimated implementation cost

### Headline

**A low-cost prototype with pay-per-use scale**

### Prototype build cost

| Item | Estimate |
|---|---:|
| Synthetic dataset and open-source stack | $0 licensing |
| Local deterministic mode | $0 external inference |
| Catalyst free-tier-eligible demo usage | Verify in team account |
| Mistral/Sarvam usage | Provider usage dependent |

### Public Catalyst rate references

- AppSail: **$0.08 per GB-hour** on the current pricing page
- API Gateway: **$0.000001 per request**
- Web Client Hosting: **$0.0000004 per request**
- Data Store storage: **$0.02 per GB**

### Footnote

Rates were checked on 13 July 2026. Reconfirm at `https://catalyst.zoho.com/pricing.html` before final submission. Do not present a monthly production total until traffic, retention, memory and AI-token assumptions are approved.

## Slide 11 — Prototype snapshots

### Headline

**Working prototype, not concept art**

### Four screenshots

1. Bilingual chat with citations
2. Explain-answer audit panel
3. Area-level operations dashboard
4. Similar-case API showing shared MO elements

### Callouts

- `Cited FIR evidence`
- `Verified audit chain`
- `No individual risk scores`
- `Cross-station only`

### Speaker note

Use real screenshots from the live or local app. Avoid Figma mockups on this slide.

## Slide 12 — Prototype performance / benchmarking

### Headline

**Fast, deterministic and testable in local mode**

### Visual

Use `visuals/03_benchmark_chart.svg`.

### Measured results

- 50 sequential requests after 3 warm-ups
- 100% successful HTTP responses
- 7.97 ms mean latency
- 7.43 ms P50 latency
- 11.16 ms P95 latency
- 6.29–12.53 ms observed range
- 3/3 automated backend tests passing
- TypeScript and Vite production builds passing

### Mandatory qualifier

**Local FastAPI TestClient + SQLite + deterministic mock provider on 13 July 2026. This is an engineering smoke test, not a Catalyst production SLA, model-accuracy score, or real-data benchmark.**

## Slide 13 — Links

### Headline

**Reproduce it. Watch it. Use it.**

### Links

- GitHub public repository: `https://github.com/nischala755/KSP_DATATHON`
- Demo video, 3 minutes: `{TEAM INPUT — add final public video URL}`
- Deployed Catalyst link: `{PENDING CATALYST LOGIN AND DEPLOYMENT}`
- Optional API docs: `{LIVE_CATALYST_URL}/docs`

### QR codes

Add three QR codes: GitHub, video and live app. Test every QR code on a phone before exporting the deck.

### Submission check

The live URL must be a Zoho Catalyst/AppSail endpoint and must remain accessible without a developer machine running.

## Slide 14 — Future development

### Headline

**From prototype to governed state-wide intelligence layer**

### Phase 1 — Harden

- Managed Catalyst identity and mandatory authentication
- Data Store/PostgreSQL persistence and migration controls
- Secrets vault, endpoint authorization and immutable audit anchor
- Kannada/Kanglish evaluation with domain reviewers

### Phase 2 — Enrich

- Multilingual pgvector candidate retrieval
- Neo4j live case/person/vehicle graph
- Reviewed OCR and field-level extraction confidence
- Bhashini-compatible speech interface

### Phase 3 — Operationalize

- Investigator feedback loop and reviewed similarity thresholds
- District/state roll-up dashboards
- Evidence package export and approval workflows
- Monitoring, drift tests and governance reporting

### Speaker note

Frame the roadmap as risk reduction and operator value, not simply adding more AI.

## Slide 15 — Responsible AI and boundaries

### Headline

**What PRAHARI deliberately refuses to do**

### Guardrails

- No model-written SQL or Cypher
- No invented FIR citations
- No individual risk or propensity score
- No autonomous document persistence
- No operational action without human judgment
- No claim of real-world accuracy from synthetic data

### Closing statement

**PRAHARI supports investigators in finding evidence; it does not replace investigation, due process or accountable decision-making.**

### Visual

Use a shield at the center with six guardrail labels around it. Use yellow only for the human-review boundary.

## Slide 16 — Thank you

Retain the supplied template visual.

### Optional one-line overlay

**PRAHARI — Evidence before eloquence.**

### Final spoken close

“PRAHARI demonstrates that conversational AI can be useful in policing without giving up evidence, jurisdiction, explainability or accountability.”

