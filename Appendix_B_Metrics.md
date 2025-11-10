# Appendix B — Operational Metrics (Prometheus)

## FastAPI/Issuer/Processor

```
ctp_validation_latency_ms_bucket{le="..."}  # histogram
ctp_validation_latency_ms_sum
ctp_validation_latency_ms_count

ctp_revocation_propagation_s_bucket{method="pull|push",le="..."}
ctp_revocation_propagation_s_sum
ctp_revocation_propagation_s_count

ctp_crl_size
ctp_tokens_active
ctp_tokens_revoked_total

ctp_ledger_append_ms_bucket{le="..."}
ctp_ledger_append_failures_total
```

## Alerts (Prometheus rules examples)

```
alert: CTPValidationP99High
expr: histogram_quantile(0.99, sum(rate(ctp_validation_latency_ms_bucket[5m])) by (le)) > 0.010
for: 10m
labels: {severity: "page"}
annotations:
  description: "p99 validation latency >10ms for 10m"
  runbook_url: "RUNBOOK_URL#validation-latency"

alert: RevocationPropagationSlow
expr: histogram_quantile(0.95, sum(rate(ctp_revocation_propagation_s_bucket[5m])) by (le, method)) > 5
for: 10m
labels: {severity: "page"}
annotations:
  description: "p95 revocation propagation >5s (pull)"
```

