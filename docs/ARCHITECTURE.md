# Architecture and design rationale

## Why an intent schema instead of generated SQL

PRAHARI treats model-produced query text as untrusted. A model may only return a Pydantic `Intent` containing a small action enum and allow-listed filters. `retrieval.py` maps those fields to SQLAlchemy expressions with bound parameters and appends role-derived scope independently. Prompt injection therefore cannot ask the model to bypass jurisdiction or invent a table join. The remote providers fall back to the deterministic parser on timeout, malformed JSON, or validation failure.

Grounded generation receives retrieved rows, not the whole database. A final allow-list check rejects any bracketed FIR citation that was not retrieved. This does not prove every sentence is semantically correct, but it establishes an enforceable provenance boundary and makes unsupported record identifiers a testable failure.

## Why aggregate areas, not individual scores

Individual “risk” scores can amplify historical policing and reporting bias while looking falsely precise. PRAHARI deliberately exposes district/station aggregates and factual case links. It does not label a person as likely to offend, recommend surveillance targets, or perform predictive policing. The fairness constraint appears in the dashboard because an ethical limitation that is hidden from operators is not an effective limitation.

## Similarity

The demo scorer uses intersecting, human-readable MO elements and excludes the source station. It gives judges an inspectable reason such as “rear-window entry” rather than an unexplained cosine score. The production path would add a multilingual narrative embedding as a candidate generator, calibrate thresholds on reviewed pairs, and retain structured MO overlap as the explanation layer. Synthetic clusters are demo fixtures, not evidence of model recall or real-world accuracy.

## Audit, “blockchain,” and post-quantum signatures

Each interaction includes the question, validated intent, retrieved IDs, response, and previous hash. HMAC-SHA256 signs the entry hash in the prototype. This detects modification within the stored sequence but is not a decentralized blockchain and does not protect against an administrator replacing the database and key together. Production should place anchors in an independently controlled append-only store and replace the signer with ML-DSA using managed keys. Calling the current mechanism “post-quantum secured” would be inaccurate.

## Operational boundaries

- Every record is synthetic and clearly labeled; none is SCRB data.
- The scanned-FIR endpoint never persists extraction without confirmation.
- Remote LLM failure reduces language flexibility but cannot broaden query authority.
- Neo4j and pgvector are deployment targets; the zero-infrastructure demo does not pretend they are already the source of truth.

