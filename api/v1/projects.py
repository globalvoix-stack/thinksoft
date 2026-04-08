"""POST /v1/projects — create a new project."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.auth import get_current_user_id
from db.pool import acquire
from db.queries.projects import create_project

log = structlog.get_logger(__name__)
router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    industry: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=1000)
    mode: str = Field("autonomous", pattern="^(light|autonomous|max)$")


class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    industry: str | None
    description: str | None
    mode: str


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_route(
    body: CreateProjectRequest,
    user_id: UUID = Depends(get_current_user_id),
) -> ProjectResponse:
    log.info("api.create_project", user_id=str(user_id), name=body.name)

    async with acquire() as conn:
        project = await create_project(
            conn,
            user_id=user_id,
            name=body.name,
            industry=body.industry,
            mode=body.mode,
            description=body.description,
        )

    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        industry=project.industry,
        description=project.description,
        mode=project.mode,
    )
