from dotenv import load_dotenv

load_dotenv()
from dataclasses import dataclass
from os import getenv
from datetime import datetime, timedelta
from pydantic import BaseModel
from uuid import uuid4, UUID  # uuid4 is for random generation
from typing import Optional, Mapping, Any, Annotated
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
import mimetypes

from app.db import Stage


class XLSXFileResponse(StreamingResponse):
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None,
        filename: str = "download",
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
        # NOTE escaped quotes are needed for filenames with spaces
        self.raw_headers.append(
            (
                b"Content-Disposition",
                f'attachment; filename="{filename}.xlsx"'.encode("latin-1"),
            )
        )


class FileResponse(StreamingResponse):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None,
        filename: str = "download.txt",
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
        # NOTE escaped quotes are needed for filenames with spaces
        self.raw_headers.append(
            (
                b"Content-Disposition",
                f'attachment; filename="{filename}"'.encode("latin-1"),
            )
        )


class NonExistant(Exception): ...


class Expired(Exception): ...


class CustomerIDNotMatch(Exception): ...


## Downloads
class DownloadLink(BaseModel):
    downloadLink: str


@dataclass
class DownloadRequest:
    customer_id: int
    download_id: UUID
    expires_at: float
    stage: Optional[Stage] = None
    s3_path: Optional[str] = None

    def __hash__(self) -> int:
        return self.download_id.__hash__()

    def expired(self) -> bool:
        return datetime.now() > self.expires_at

    def __eq__(self, other) -> bool:
        return self.download_id == other


class DownloadIDs:
    active_requests: set[DownloadRequest] = set()

    @classmethod
    def generate_id(
        cls, customer_id: int, stage: Stage = None, s3_path: str = None
    ) -> str:
        value = uuid4()
        duration = timedelta(float(getenv("DL_LINK_DURATION")) * 60)
        expiry = datetime.now() + duration
        request = DownloadRequest(
            customer_id=customer_id,
            stage=stage,
            download_id=value,
            expires_at=expiry,
            s3_path=s3_path,
        )
        cls.active_requests.add(request)
        return str(request.download_id)

    @classmethod
    def use_download(cls, customer_id: int, id_value: str) -> DownloadRequest:
        incoming_uuid: UUID = UUID(id_value)
        if incoming_uuid in cls.active_requests:
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
