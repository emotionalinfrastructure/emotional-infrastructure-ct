# Executive Brief — Consent Token Protocol (CTP) Pilot

**Program:** Emotional Infrastructure™ · **Owner:** Brittany Wright  
**Artifact:** Pilot Readiness & Commitments (Partner-Facing)  
**Version:** 1.0 · **Date:** 2025-11-10

---

## 1) Purpose
Deploy CTP v0.1 with a pilot partner to **prove enforceable, revocable consent** for emotional/behavioral processing at production-like scale, with full auditability and measurable SLOs.

## 2) Scope (What’s In)
- Token issuance, validation, revocation
- Append-only audit ledger (hash-chained) with weekly Merkle anchoring
- Observability: Prometheus metrics, Grafana dashboard, alert rules
- Performance SLOs and error budgets

**Out of Scope (v0.1):**
- Multi-region failover, advanced UI/UX experiments, facial biometrics

## 3) Success Criteria (Go/No-Go)
**Technical**
- p99 validation latency ≤ 10ms (daily SLO)
- Revocation propagation p95 ≤ 1s (push) / ≤ 5s (pull)
- ≥ 99.5% service uptime
- 100% ledger integrity (no broken chains)

**Business**
- ≥ 70% user consent rate
- ≤ 5% user revocation rate
- Integration completed in ≤ 40 developer-hours

## 4) Responsibilities
**Partner**
- Build consent UI (plain-language, WCAG AA)
- Send ContextEnvelope to `/issue`; call `/introspect` before protected ops
- Wire **Revoke** control to `/revoke`
- Participate in weekly check-ins; surface user feedback

**CTP Team**
- Operate issuance/validation/revocation services and ledger
- Provide JWKS, push revocation channel, metrics, and dashboards
- Maintain SLOs; respond to alerts
- Deliver weekly status + end-of-pilot report

## 5) Timeline
- **Weeks 1–2:** Hardening (KMS/HSM, WebSocket revocation, staging)  
- **Weeks 3–4:** Partner onboarding (integration workshop, UI and policy review)  
- **Month 2:** Pilot launch (50 users → scale)  
- **Months 3–6:** Iterate, optimize, compliance audit prep

## 6) Risk & Mitigation
- **Key compromise (Critical):** Cloud KMS/HSM, 90‑day rotation, dual control
- **Revocation lag (High):** Push channel with 1s target, fallback polling
- **Ledger growth (Medium):** Hot/warm/cold tiers + archival pipeline
- **Clock skew (Medium):** NTP enforcement, 60s drift tolerance

## 7) Artifacts Delivered
- Repo (spec, API, demo, ledger schema)
- **Pilot Partner Integration Guide**
- **Grafana dashboard JSON**
- **Prometheus alert rules** (this document references `infra/prometheus_alerts_ctp_slos.yaml`)

## 8) Sign-Off
- **Partner Lead:** ____________________  Date: __________
- **CTP Tech Lead:** ___________________  Date: __________
- **CTP Program Owner:** Brittany Wright  Date: __________

---

**Contact:** press@emotionalinfrastructure.org | www.emotionalinfrastructure.org
