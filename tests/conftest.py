# plexport has no .py extension, so it can't be imported from sys.path;
# load it explicitly and register it so tests can `import plexport`.
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_loader = importlib.machinery.SourceFileLoader(
    "plexport", str(Path(__file__).resolve().parent.parent / "plexport")
)
_spec = importlib.util.spec_from_loader("plexport", _loader)
_module = importlib.util.module_from_spec(_spec)
sys.modules["plexport"] = _module
_loader.exec_module(_module)
