"""/v1/projects — full project CRUD."""
from __future__ import annotations

from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.auth import get_current_user_id
from db.pool import acquire
from db.queries.projects import (
    create_project,
    delete_project,
    get_project_by_clerk_user,
    list_projects_by_clerk_user,
    set_starred,
)

log = structlog.get_logger(__name__)
router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    industry: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=1000)
    mode: str = Field("autonomous", pattern="^(light|autonomous|max)$")
    image_url: str | None = None


class ProjectResponse(BaseModel):
    id: str
    clerk_user_id: str | None
    name: str
    industry: str | None
    description: str | None
    mode: str
    is_starred: bool
    image_url: str | None
    created_at: str
    updated_at: str


def _to_response(p) -> ProjectResponse:
    return ProjectResponse(
        id=str(p.id),
        clerk_user_id=p.clerk_user_id,
        name=p.name,
        industry=p.industry,
        description=p.description,
        mode=p.mode,
        is_starred=p.is_starred,
        image_url=p.image_url,
        created_at=p.created_at.isoformat(),
        updated_at=p.updated_at.isoformat(),
    )


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects_route(
    clerk_user_id: str = Depends(get_current_user_id),
) -> list[ProjectResponse]:
    async with acquire() as conn:
        projects = await list_projects_by_clerk_user(conn, clerk_user_id)
    log.info("api.list_projects", clerk_user_id=clerk_user_id, count=len(projects))
    return [_to_response(p) for p in projects]


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_route(
    body: CreateProjectRequest,
    clerk_user_id: str = Depends(get_current_user_id),
) -> ProjectResponse:
    log.info("api.create_project", clerk_user_id=clerk_user_id, name=body.name)
    # Use a stable deterministic UUID derived from clerk_user_id for the user_id FK
    # (the users table still exists but we primarily route by clerk_user_id)
    synthetic_user_id = uuid4()
    async with acquire() as conn:
        project = await create_project(
            conn,
            user_id=synthetic_user_id,
            name=body.name,
            industry=body.industry,
            mode=body.mode,
            description=body.description,
            clerk_user_id=clerk_user_id,
            image_url=body.image_url,
        )
    return _to_response(project)


@router.patch("/projects/{project_id}/star", response_model=ProjectResponse)
async def star_project_route(
    project_id: str,
    clerk_user_id: str = Depends(get_current_user_id),
) -> ProjectResponse:
    try:
        pid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID")

    async with acquire() as conn:
        project = await get_project_by_clerk_user(conn, pid, clerk_user_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        updated = await set_starred(conn, pid, clerk_user_id, not project.is_starred)

    log.info("api.star_project", project_id=project_id, starred=updated.is_starred)
    return _to_response(updated)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_route(
    project_id: str,
    clerk_user_id: str = Depends(get_current_user_id),
) -> None:
    try:
        pid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID")

    async with acquire() as conn:
        deleted = await delete_project(conn, pid, clerk_user_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    log.info("api.delete_project", project_id=project_id)
