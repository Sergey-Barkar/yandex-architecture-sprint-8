import random, string, httpx
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_headers=["*"], allow_methods=["*"], allow_origins=["*"])

async def getKey():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://keycloak:8080/realms/reports-realm/protocol/openid-connect/certs")
        response.raise_for_status()
        return response.json()["keys"][1]

async def decode(_token: str, _audience: str):
    key = await getKey()
    return jwt.decode(_token, key, algorithms=["RS256"], audience=_audience)

async def getUser(_credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    token = await decode(_credentials.credentials, "reports-frontend")

    if "prothetic_user" in token.get("realm_access", {}).get("roles", []):
        return token
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

def getReportsData():
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(7))

@app.get("/reports")
async def getReport(_user: dict = Depends(getUser)):
    return JSONResponse(content={"reports": getReportsData()})