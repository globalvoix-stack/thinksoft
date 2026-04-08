"""API v1 routes."""
from fastapi import APIRouter
from api.v1 import context, files, generate, memory, projects, scan, stream

router = APIRouter(prefix="/v1")
router.include_router(projects.router, tags=["projects"])
router.include_router(generate.router, tags=["generate"])
router.include_router(stream.router, tags=["stream"])
router.include_router(files.router, tags=["files"])
router.include_router(memory.router, tags=["memory"])
router.include_router(context.router, tags=["context"])
router.include_router(scan.router, tags=["scan"])
