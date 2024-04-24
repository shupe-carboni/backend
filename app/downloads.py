
from dotenv import load_dotenv; load_dotenv()
from dataclasses import dataclass
from os import getenv
from datetime import datetime, timedelta
from uuid import uuid4, UUID  # uuid4 is for random generation

from app.db import Stage

class NonExistant(Exception):...
class Expired(Exception):...
class CustomerIDNotMatch(Exception):...

@dataclass
class DownloadRequest:
    customer_id: int
    stage: Stage
    download_id: UUID
    expires_at: float

    def __hash__(self) -> int:
        return self.download_id.__hash__()
    
    def expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def __eq__(self, other) -> bool:
        return self.download_id == other

class DownloadIDs:
    active_requests: set[DownloadRequest] = set()

    @classmethod
    def generate_id(cls, customer_id: int, stage: Stage) -> str:
        value = uuid4()
        duration = timedelta(float(getenv('DL_LINK_DURATION'))*60)
        expiry = datetime.now() + duration
        request = DownloadRequest(
            customer_id=customer_id,
            stage=stage,
            download_id=value,
            expires_at=expiry
        )
        cls.active_requests.add(request)
        return str(request.download_id)
    
    @classmethod
    def use_download(cls, customer_id: int, id_value: str) -> DownloadRequest:
        incoming_uuid: UUID = UUID(id_value)
        for stored_request in cls.active_requests:
            if stored_request == incoming_uuid:
                if stored_request.customer_id == customer_id:
                    if not stored_request.expired():
                        cls.active_requests.remove(stored_request)
                        return stored_request
                    else:
                        raise Expired
                else:
                    raise CustomerIDNotMatch
        raise NonExistant