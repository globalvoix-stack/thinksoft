"""
Thinksoft job queue and SSE module - empty for now.

IMPORTANT: This package re-exports Python stdlib queue contents to prevent
shadowing issues when the project root is in sys.path.
"""
import sys as _sys
import importlib.util as _util

# Re-export stdlib queue by loading it from its spec before our package shadows it
_stdlib_spec = _util.find_spec('queue', package=None)
# Bypass our own package to find the stdlib version
_stdlib_paths = [
    p for p in _sys.path
    if p and 'thinksoft' not in p.lower().replace('\\', '/')
]

# Load stdlib queue directly from its source file
_stdlib_source = None
for _path in _stdlib_paths:
    import os as _os
    _candidate = _os.path.join(_path, 'queue.py')
    if _os.path.isfile(_candidate):
        _stdlib_source = _candidate
        break

if _stdlib_source:
    _spec = _util.spec_from_file_location('_stdlib_queue', _stdlib_source)
    _stdlib_queue = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_stdlib_queue)
    # Re-export all public names from stdlib queue
    SimpleQueue = _stdlib_queue.SimpleQueue
    Queue = _stdlib_queue.Queue
    PriorityQueue = _stdlib_queue.PriorityQueue
    LifoQueue = _stdlib_queue.LifoQueue
    Empty = _stdlib_queue.Empty
    Full = _stdlib_queue.Full
