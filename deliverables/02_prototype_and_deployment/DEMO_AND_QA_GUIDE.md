# Three-minute demo and judge Q&A guide

## Demo script

### 0:00–0:20 — Problem and promise

“Crime patterns do not stop at police-station boundaries. PRAHARI lets an authorized officer ask in English or Kannada, retrieve cited FIR evidence, discover explainable cross-station MO links, and audit every answer.”

### 0:20–0:55 — Grounded query

Ask:

```text
How many IPC 420 cases are in Mysuru?
```

Say:

“The result is not free-form database generation. PRAHARI produced a validated intent containing district, IPC section and aggregate action. Trusted code built the query. Each visible FIR chip comes from the retrieved set.”

### 0:55–1:15 — Kannada

Ask:

```text
ಮೈಸೂರು ಜಿಲ್ಲೆಯಲ್ಲಿ ಎಷ್ಟು ಪ್ರಕರಣಗಳು?
```

Say:

“The offline parser keeps the prototype demonstrable without an external dependency. The provider switch supports Mistral or Sarvam for broader language coverage.”

### 1:15–1:50 — Cross-station similarity

Open a case's similar endpoint or linked-cases view.

Say:

“We exclude the source station and show the exact overlap—such as rear-window entry, night-time and jewellery targeting. The investigator sees why the case was surfaced.”

### 1:50–2:20 — Audit

Click **Explain this answer**.

Say:

“Every turn records the query, validated intent, retrieved IDs and answer. Each record links to the previous hash and has a signature-verification status.”

### 2:20–2:40 — Responsible analytics

Open Operations Overview.

Say:

“PRAHARI deliberately shows area aggregates instead of individual risk scores. It supports investigation; it does not predict who will offend.”

### 2:40–3:00 — Deployment and close

Say:

“The full React and FastAPI application is deployed as one service on Zoho Catalyst AppSail. All 500 FIRs are synthetic. Our next step is governed data integration and investigator-reviewed similarity calibration.”

## Likely judge questions

### “How do you prevent hallucinations?”

Do not say “we eliminate hallucinations.” Say:

“We constrain the model to an intent schema, build queries in trusted code, generate from retrieved context, reject unknown FIR citations and abstain when no records match. These controls reduce unsupported output and make provenance enforceable, but human verification remains required.”

### “Why not let the model generate SQL?”

“Because prompt wording is not an authorization boundary. A model-generated query could be unsafe, hard to reproduce and difficult to scope. Our intent object provides a small testable interface between language and data.”

### “Is the similarity AI?”

“The current demo uses structured, explainable MO overlap to remain inspectable. The production design uses multilingual embeddings to retrieve candidates and keeps the structured overlap as the explanation layer. We do not claim a real-world accuracy score from synthetic clusters.”

### “What is unique?”

“The combination: bilingual access, deterministic role-scoped retrieval, citation allow-listing, explainable cross-station MO discovery and a signed interaction chain. It is an accountability architecture, not just a chat interface.”

### “What Catalyst services are actually used?”

“The submitted live service uses AppSail. Data Store, managed Authentication, API Gateway, Stratus, Cache and Pipelines are our production migration path, not claims about the current prototype.”

### “What happens when Mistral or Sarvam is unavailable?”

“The adapter catches timeout, API, JSON and schema failures and falls back to the deterministic parser. Availability degrades language flexibility, not database authority.”

### “How is sensitive information protected?”

“The demo contains no sensitive data. Production requires mandatory authentication, field-level redaction, encryption, managed secrets, row-level security, independent audit anchoring, retention policies and security review.”

### “Can the audit be tampered with?”

“The current hash chain detects modification, deletion and reordering when verified against the same chain and signing key. It is not a blockchain and does not protect against an administrator replacing both database and key. Production requires externally controlled immutable anchors and ML-DSA managed keys.”

### “What is your impact metric?”

“The prototype measures technical safety and latency, not policing outcomes. A controlled pilot should measure investigator time-to-find linked records, precision of reviewed similarity suggestions, abstention quality, language usability and false-link review burden.”

