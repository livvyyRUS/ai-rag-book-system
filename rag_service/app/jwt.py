import os
import jwt
from src.models.jwt_payload import JWTPayload

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "secret_key")

def encode_jwt(payload: JWTPayload):
    return jwt.encode(payload=payload.model_dump(), key=SECRET_KEY)

def decode_jwt(jwt_token: str):
    answer = jwt.decode(jwt=jwt_token, key=SECRET_KEY)
    return JWTPayload.model_validate(answer)