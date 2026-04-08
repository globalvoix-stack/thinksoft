"""
Thinksoft job queue and SSE module.

Public API (queue.manager):
  enqueue(project_id, session_id, mode) — create a pending job
  start(job_id)                         — transition to running
  progress(job_id, pct, message)        — update progress
  complete(job_id, result)              — mark done
  fail(job_id, error)                   — mark failed
  get(job_id)                           — fetch job by ID
  list_for_project(project_id)          — recent jobs
  sweep_stale()                         — timeout stuck jobs
  run_with_timeout(job_id, coro)        — run with auto-fail on timeout

Public API (queue.sse):
  stream_job_sse_starlette(job_id)      — async generator for EventSourceResponse

IMPORTANT: This package also re-exports Python stdlib queue contents to prevent
shadowing issues when the project root is in sys.path.
"""
import sys as _sys
import importlib.util as _util
import os as _os

# Re-export stdlib queue by loading it from its source file
_stdlib_paths = [
    p for p in _sys.path
    if p and 'thinksoft' not in p.lower().replace('\\', '/')
]

_stdlib_source = None
for _path in _stdlib_paths:
    _candidate = _os.path.join(_path, 'queue.py')
    if _os.path.isfile(_candidate):
        _stdlib_source = _candidate
        break

if _stdlib_source:
    _spec = _util.spec_from_file_location('_stdlib_queue', _stdlib_source)
    _stdlib_queue = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_stdlib_queue)
    SimpleQueue = _stdlib_queue.SimpleQueue
    Queue = _stdlib_queue.Queue
    PriorityQueue = _stdlib_queue.PriorityQueue
    LifoQueue = _stdlib_queue.LifoQueue
    Empty = _stdlib_queue.Empty
    Full = _stdlib_queue.Full
