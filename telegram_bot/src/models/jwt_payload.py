from pydantic import BaseModel

class JWTPayload(BaseModel):
    user_id: str