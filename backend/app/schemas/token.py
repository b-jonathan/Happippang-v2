from pydantic import BaseModel


class RefreshToken(BaseModel):
    refresh_token: str


class Token(RefreshToken):
    access_token: str
    token_type: str
