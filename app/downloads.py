from dotenv import load_dotenv

load_dotenv()
from dataclasses import dataclass
from os import getenv
from datetime import datetime, timedelta
from pydantic import BaseModel
from uuid import uuid4, UUID  # uuid4 is for random generation
from typing import Optional, Mapping, Any, Callable
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status

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


class NonExistant(HTTPException):
    def __init__(self) -> None:
        status_code = status.HTTP_404_NOT_FOUND
        super().__init__(status_code=status_code)


class Expired(HTTPException):
    def __init__(self) -> None:
        status_code = status.HTTP_400_BAD_REQUEST
        msg = "This link has expired"
        super().__init__(status_code=status_code, detail=msg)


class ResourceIDNotMatch(HTTPException):
    def __init__(self) -> None:
        status_code = status.HTTP_400_BAD_REQUEST
        msg = "The resource ID does not match the id associated with this link"
        super().__init__(status_code=status_code, detail=msg)


## Downloads
class DownloadLink(BaseModel):
    downloadLink: str


@dataclass
class DownloadRequest:
    resource: str
    stage: Optional[Stage] = None
    s3_path: Optional[str] = None
    callback: Optional[Callable] = None

    def __hash__(self) -> int:
        return self.download_id.__hash__()

    def __post_init__(self) -> None:
        duration = timedelta(float(getenv("DL_LINK_DURATION")) * 60)
        self.expires_at = datetime.now() + duration
        self.download_id = uuid4()

    def __bool__(self) -> bool:
        return datetime.now() <= self.expires_at

    def __eq__(self, other) -> bool:
        return self.download_id == other


class DownloadIDs:
    active_requests: dict[int, DownloadRequest] = dict()

    @classmethod
    def add_request(
        cls,
        resource: str,
        stage: Stage = None,
        s3_path: str = None,
        callback: Callable = None,
    ) -> str:
        request = DownloadRequest(
            resource=resource, stage=stage, s3_path=s3_path, callback=callback
        )
        cls.active_requests.update({hash(request): request})
        return str(request.download_id)

    @classmethod
    def use_download(cls, resource: str, id_value: str) -> DownloadRequest:
        incoming_uuid: int = hash(UUID(id_value))
        try:
            stored_request = cls.active_requests.pop(incoming_uuid)
        except KeyError:
            raise NonExistant
        else:
            if stored_request and stored_request.resource == resource:
                return stored_request
            elif not stored_request:
                raise Expired
            else:
                raise ResourceIDNotMatch
