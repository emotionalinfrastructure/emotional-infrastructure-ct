from fastapi import FastAPI, HTTPException
import jwt, time

app = FastAPI()

@app.post("/token/validate")
def validate_token(token: str):
    try:
        decoded = jwt.decode(token, "secret", algorithms=["HS256"])
        if decoded.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Expired")
        return {"valid": True, "claims": decoded}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))