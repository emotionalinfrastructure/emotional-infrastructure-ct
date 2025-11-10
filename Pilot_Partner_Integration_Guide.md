# Pilot Partner Integration Guide — Consent Token Protocol (CTP) v0.1

**Author:** Brittany Wright · Emotional Infrastructure™  
**Scope:** This guide enables a partner engineering team to integrate CTP in ≤ 40 developer‑hours.

---

## 1) Integration Overview

CTP enforces **cryptographic, revocable consent** for emotional/behavioral signal processing. Partners integrate three interfaces:

1. **Issue** — obtain a short‑lived, purpose‑bound token after explicit consent
2. **Introspect** — validate token + context before each protected operation
3. **Revoke** — withdraw consent and propagate denial network‑wide

> Tokens are **JWTs** (ES256 recommended in production). Context is **hash‑bound** to prevent replay across channels, features, or purposes.

---

## 2) Endpoints & Schemas (OpenAPI)

OpenAPI spec is included at: `openapi/ctp-api.yaml`

- **POST `/issue`** — Request body: `ContextEnvelope`  
  Response: `{ token, jti }`
- **POST `/introspect`** — Request body: `{ token, context_envelope }`  
  Response: `{ active, decision, reason, sub, jti, scope, purpose }`
- **POST `/revoke`** — Request body: `{ jti, reason? }`  
  Response: `{ status: "ok", revoked: "<jti>" }`
- **GET `/.well-known/jwks.json`** — ES256 public keys (production)

**ContextEnvelope** (minimal, privacy‑preserving)
```json
{
  "ts": "2025-11-09T20:17:00Z",
  "channel": "voice",
  "features": ["tone","sentiment"],
  "processor": "svc://cx-ai/v1",
  "purpose": "customer_retention",
  "retention": "session_only",
  "jurisdiction": "US-KY",
  "ui_copy_id": "consent-modal-2025-11-01#en-US"
}
```

---

## 3) Implementation Steps

### A. Consent UI (Partner-owned)
- Present short, plain-language consent for the specific **purpose** and **features** (WCAG 2.1 AA).
- On “Agree,” POST the **ContextEnvelope** to `/issue` and cache `{token, jti}` for **≤ 300s**.
- Re‑issue on scope/purpose change or expiry; expose “Revoke” clearly.

**Suggested copy (example):**
> “With your permission, we will analyze **tone** and **sentiment** in this call for **customer support quality**. Your consent lasts for this session and can be revoked anytime.”

### B. Pre‑processing Check
Before **every** protected operation, call `/introspect`:
- Build the same ContextEnvelope used at issuance (or updated if purpose changes).
- If `decision: deny`, do not process and surface a user-friendly message.

### C. Revocation
- Call `/revoke` with the **JTI**.
- Expect propagation in **≤ 5s** (pull) or **≤ 1s** (push).
- Update UI to reflect revoked state immediately.

---

## 4) Request Examples (cURL)

**Issue**
```bash
curl -s http://127.0.0.1:8000/issue -H "Content-Type: application/json" -d '{
  "ts":"2025-11-09T20:17:00Z",
  "channel":"voice",
  "features":["tone","sentiment"],
  "processor":"svc://cx-ai/v1",
  "purpose":"customer_retention",
  "retention":"session_only",
  "jurisdiction":"US-KY",
  "ui_copy_id":"consent-modal-2025-11-01#en-US"
}'
```

**Introspect**
```bash
TOKEN="eyJhbGciOi..."
curl -s http://127.0.0.1:8000/introspect -H "Content-Type: application/json" -d "{
  "token": "$TOKEN",
  "context_envelope": {
    "ts":"2025-11-09T20:17:00Z",
    "channel":"voice",
    "features":["tone","sentiment"],
    "processor":"svc://cx-ai/v1",
    "purpose":"customer_retention",
    "retention":"session_only",
    "jurisdiction":"US-KY",
    "ui_copy_id":"consent-modal-2025-11-01#en-US"
  }
}"
```

**Revoke**
```bash
curl -s http://127.0.0.1:8000/revoke -H "Content-Type: application/json"   -d '{"jti":"c0b3e1f8-4567-4890-abcd-1234567890ab","reason":"user_revoked"}'
```

---

## 5) Token Header & Claims (Quick Reference)

**Header**
```json
{ "alg": "ES256", "kid": "key-2025-11" }
```
**Required Claims**
```json
{
  "iss": "https://partner.example/consent",
  "aud": "svc://cx-ai/v1",
  "sub": "pairwise-pseudonymous-id",
  "iat": 1731200220,
  "exp": 1731200460,
  "jti": "uuid-v4",
  "scope": ["tone.read","sentiment.read"],
  "purpose": "customer_retention",
  "context_hash": "sha256(hex)",
  "policy_uri": "https://partner.example/policy/2025-11-01",
  "consent_level": "explicit",
  "consent_version": "ctp-0.1"
}
```

---

## 6) Validation Rules (Server-side)

- Verify signature against JWKS; require `exp`, `iat`, `jti`, `aud`, `iss`
- Enforce **clock skew ≤ 60s**
- Deny on: expired token, **revoked `jti`**, audience mismatch
- Recompute `context_hash`; deny on mismatch
- Enforce `scope` + `purpose` before processing

**Performance SLO:** p99 validation ≤ **10ms** (with warm caches)

---

## 7) Observability & Alerting

Export the following metrics (Prometheus names aligned with Appendix B):
- `ctp_token_validation_latency_seconds{quantile="0.99"}`
- `ctp_revocation_propagation_seconds`
- `ctp_ledger_append_latency_seconds`
- `ctp_validation_errors_total{reason}`

**Alerts (burn-rate style):**
- **Critical:** p99 validation ≥ 10ms for 10 minutes
- **Critical:** revocation propagation p95 ≥ 5s (pull) or ≥ 1s (push) for 5 minutes
- **Warning:** validation errors ≥ 0.5% for 10 minutes

A starter Grafana dashboard JSON is included at `infra/grafana_ctp_revocation_dashboard.json`.

---

## 8) Security & Key Management (Production)

- Use **ES256** with **cloud KMS/HSM**; publish `/.well-known/jwks.json`
- Rotate keys every **90 days** with **dual control**
- Enforce **TLS 1.2+**, HSTS, and secure cookie flags where applicable
- Maintain a **CRL** in Redis + push revocation channel (SSE/WebSocket)

---

## 9) Data & Ledger

- Append‑only, hash‑chained ledger (hot → warm → cold)
- Weekly **Merkle anchoring** to an external timestamping authority
- Hot tier retention: **90 days**; warm: **1 year**; cold: **7 years**

---

## 10) Validation Checklist (Cutover Gate)

**Functional**
- [ ] Issue, Introspect, Revoke endpoints return 200 with valid payloads
- [ ] p99 validation ≤ 10ms @ 1k rps
- [ ] Revocation propagation p95 ≤ 1s (push) / ≤ 5s (pull)

**Security**
- [ ] ES256 keys in KMS/HSM; JWKS served in prod
- [ ] Key rotation runbook executed in staging
- [ ] TLS verified; OWASP ZAP scan clean

**Compliance**
- [ ] Consent UI tested (WCAG AA); GDPR Art. 7 mapping complete
- [ ] Ledger audit export validated
- [ ] Privacy impact assessment approved

---

## 11) Support & Ownership

- **Partner team owns** the Consent UI and purpose strings  
- **Your CTP service** owns token issuance, validation, revocation, and the ledger  
- Shared on-call escalation: revocation propagation, JWKS availability, and SLOs

---

**Version:** 1.0 · **Last updated:** 2025‑11‑09
