from pydantic import BaseModel

# Request from frontend to exchange public token for access token
class PublicTokenRequest(BaseModel):
    public_token: str

# Response: access token and item ID after exchange
class TokenExchangeResponse(BaseModel):
    access_token: str
    item_id: str

# Link Token response to be sent to frontend
class LinkTokenResponse(BaseModel):
    link_token: str
