# Appendix C — Key Rotation Runbook

**Objective:** Rotate CTP signing keys with zero downtime and full auditability.

## Preconditions
- HSM/KMS keys created (new key version enabled, not primary)
- JWKS can expose both old and new `kid` during grace
- Dual-control approval recorded

## Steps
1. **Prepare**
   - Generate new key version in KMS
   - Add new JWK to JWKS endpoint with `status=staged` and new `kid`
   - Configure validator caches to refresh JWKS every 60s with jitter

2. **Enable Dual-Validation**
   - Issuer continues signing with **old** key
   - Validators accept **old + new** keys (grace start)

3. **Switch Issuer**
   - Flip issuer to sign with **new** key
   - Monitor validation success, error rates, and token issuance

4. **Grace Period**
   - Maintain dual-acceptance for 24h (configurable based on TTLs)
   - Watch for stragglers and clock skew anomalies

5. **Retire Old Key**
   - Remove old `kid` from JWKS
   - Revoke old key version in KMS (disable sign), keep for verify-only if policy requires

6. **Audit**
   - Append ledger events for: staged, switchover, retired
   - Export rotation report including token success rates and any failures
