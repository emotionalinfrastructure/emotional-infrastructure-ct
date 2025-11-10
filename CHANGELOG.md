# Changelog

All notable changes to this project will be documented in this file.  
This format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)  
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v0.1.0] — 2025-11-10
### Pilot Ready Build

**Added**
- JWT-based consent token specification
- Real-time consent enforcement (p99 6.2 ms)
- Revocation push channel (pilot implementation)
- Audit ledger + technical specification + operational runbook
- Docker Compose setup with Prometheus + Grafana for observability

**Security**
- Short token TTL (≤ 300s) with context hashing
- Pairwise pseudonymous identifiers for privacy protection
- Rotating key validation for token issuance and verification

**Meta**
- First public release of *Emotional Infrastructure™ — Consent Token Protocol (CTP)*
- Developed and authored by **Brittany Wright**

---
