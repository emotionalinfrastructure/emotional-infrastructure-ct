import os, json, time, uuid, hmac, hashlib
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
import jwt

# DEMO ONLY: HS256 secret; replace with ES256 + KMS in prod
CTP_SECRET = os.getenv("CTP_SECRET", "dev-local-secret")
AUDIENCE = os.getenv("CTP_AUDIENCE", "svc://cx-ai/v1")
CLOCK_SKEW = 60
TTL_SECONDS = 240

# In-memory CRL and ledger (demo)
CRL = set()
LEDGER = []
KID = "demo-hs256"

def canon_hash(envelope: dict) -> str:
    # canonical JSON (sorted keys, no whitespace)
    s = json.dumps(envelope, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

class ContextEnvelope(BaseModel):
    ts: str
    channel: str
    features: List[str]
    processor: str
    purpose: str
    retention: str
    jurisdiction: str
    ui_copy_id: str

class IssueResponse(BaseModel):
    token: str
    jti: str

class IntrospectRequest(BaseModel):
    token: str
    context_envelope: ContextEnvelope

class IntrospectResponse(BaseModel):
    active: bool
    sub: Optional[str]
    jti: Optional[str]
    scope: Optional[List[str]]
    purpose: Optional[str]
    decision: str
    reason: Optional[str]

class RevokeRequest(BaseModel):
    jti: str
    reason: Optional[str] = None

app = FastAPI(title="CTP Demo API")

def append_ledger(action: str, sub: str, jti: str, scopes: List[str], purpose: str, context_hash: str, policy_uri: str, decision: str):
    prev = LEDGER[-1]["hash_self"] if LEDGER else None
    payload = {
        "event_id": str(uuid.uuid4()),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "actor": AUDIENCE,
        "sub": sub,
        "jti": jti,
        "action": action,
        "scopes": scopes,
        "purpose": purpose,
        "context_hash": context_hash,
        "policy_uri": policy_uri,
        "decision": decision,
        "hash_prev": prev
    }
    # simple hash chain
    hsrc = json.dumps(payload, sort_keys=True).encode("utf-8")
    payload["hash_self"] = hashlib.sha256(hsrc).hexdigest()
    LEDGER.append(payload)

@app.post("/issue", response_model=IssueResponse)
async def issue(envelope: ContextEnvelope, request: Request):
    now = int(time.time())
    jti = str(uuid.uuid4())
    sub = "pseud-" + uuid.uuid4().hex[:8]
    scope = ["tone.read", "sentiment.read"]
    policy_uri = "https://rp.example/policy/2025-11-01"
    claims = {
        "iss": "https://rp.example/consent",
        "aud": AUDIENCE,
        "sub": sub,
        "iat": now,
        "exp": now + TTL_SECONDS,
        "jti": jti,
        "scope": scope,
        "purpose": envelope.purpose,
        "context_hash": canon_hash(envelope.dict()),
        "policy_uri": policy_uri,
        "consent_level": "explicit",
        "consent_version": "ctp-0.1",
        "kid": KID
    }
    token = jwt.encode(claims, CTP_SECRET, algorithm="HS256", headers={"kid": KID})
    append_ledger("access", sub, jti, scope, envelope.purpose, claims["context_hash"], policy_uri, "allow")
    return {"token": token, "jti": jti}

@app.post("/introspect", response_model=IntrospectResponse)
async def introspect(req: IntrospectRequest):
    # Signature / time checks
    try:
        hdrs = jwt.get_unverified_header(req.token)
        if hdrs.get("kid") != KID:
            raise HTTPException(status_code=401, detail="Unknown key id")
        payload = jwt.decode(req.token, CTP_SECRET, algorithms=["HS256"], audience=AUDIENCE, options={"require": ["exp","iat","jti","aud","iss"]})
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    now = int(time.time())
    if abs(now - payload["iat"]) > CLOCK_SKEW:
        return IntrospectResponse(active=False, decision="deny", reason="clock_skew")

    # Revocation
    if payload["jti"] in CRL:
        return IntrospectResponse(active=False, decision="deny", reason="revoked")

    # Context binding
    ctx_hash = canon_hash(req.context_envelope.dict())
    if ctx_hash != payload["context_hash"]:
        return IntrospectResponse(active=False, decision="deny", reason="context_mismatch")

    # Scope/purpose (demo: accept)
    return IntrospectResponse(
        active=True,
        sub=payload["sub"],
        jti=payload["jti"],
        scope=payload.get("scope", []),
        purpose=payload.get("purpose"),
        decision="allow",
        reason=None
    )

@app.post("/revoke")
async def revoke(req: RevokeRequest):
    CRL.add(req.jti)
    return {"status": "ok", "revoked": req.jti}

@app.get("/.well-known/jwks.json")
async def jwks():
    # Demo HS256 doesn't publish a JWKS. ES256 would publish JWK here.
    return {"keys": []}

@app.get("/ledger")
async def ledger():
    return {"events": LEDGER}
