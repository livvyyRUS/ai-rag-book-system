import os
import datetime

import jwt
from pydantic import BaseModel

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "secret_key")
# print(SECRET_KEY)

class JWTPayload(BaseModel):
    user_id: str
    exp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)

def encode_jwt(payload: JWTPayload):
    return jwt.encode(payload=payload.model_dump(), key=SECRET_KEY, algorithm="HS256")

def decode_jwt(jwt_token: str) -> JWTPayload:
    answer = jwt.decode(jwt=jwt_token, key=SECRET_KEY, algorithms=["HS256"])
    return JWTPayload.model_validate(answer)

