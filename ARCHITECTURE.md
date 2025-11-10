# Architecture Overview (CTP)

CTP enforces **cryptographic consent** with auditability and low latency.

**Core components**
- **Issuer** (`issuer.py`): mints signed tokens (JWT/JWS). Integrates with KMS/HSM in production.
- **Processor/Server** (`server.py`): validates tokens, checks CRL, records ledger events.
- **Ledger** (`ledger.sql`): append-only event store (moving to Postgres in production).
- **Revocation Channel**: polling or push (WebSocket/SSE).
- **Observability**: Prometheus metrics, Grafana dashboard.

**Security-in-Depth**
- Context-bound tokens, strict scopes, short TTLs, fast revocation.
- Key rotation grace window; dual-key validation during transition.
