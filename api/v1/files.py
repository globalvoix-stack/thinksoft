"""GET /v1/files — retrieve generated files for a project."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.auth import get_current_user_id
from db.pool import acquire
from db.queries.files import GeneratedFile, get_file, get_job_files, get_project_files
from db.queries.projects import get_project

log = structlog.get_logger(__name__)
router = APIRouter()


class FileResponse(BaseModel):
    id: UUID
    file_path: str
    content: str
    language: str | None
    version: int


@router.get("/files", response_model=list[FileResponse])
async def list_files_route(
    project_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> list[FileResponse]:
    async with acquire() as conn:
        project = await get_project(conn, project_id, user_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        files = await get_project_files(conn, project_id)

    log.info("api.list_files", project_id=str(project_id), count=len(files))
    return [
        FileResponse(
            id=f.id,
            file_path=f.file_path,
            content=f.content,
            language=f.language,
            version=f.version,
        )
        for f in files
    ]


@router.get("/files/job/{job_id}", response_model=list[FileResponse])
async def list_job_files_route(
    job_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> list[FileResponse]:
    async with acquire() as conn:
        files = await get_job_files(conn, job_id)

    return [
        FileResponse(
            id=f.id,
            file_path=f.file_path,
            content=f.content,
            language=f.language,
            version=f.version,
        )
        for f in files
    ]
