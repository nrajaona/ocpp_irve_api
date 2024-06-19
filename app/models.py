from pydantic import BaseModel
from typing import Optional

class StatusResponse(BaseModel):
    connectorId: int
    errorCode: str
    status: str
    timestamp: str
    info: Optional[str] = None
    vendorId: Optional[str] = None
    vendorErrorCode: Optional[str] = None