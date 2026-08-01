# plexport has no .py extension, so it can't be imported from sys.path;
# load it explicitly and register it so tests can `import plexport`.
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent

# test_script_metadata imports the sync script so the parser and the writer of
# the PEP 723 block can't drift apart.
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

_loader = importlib.machinery.SourceFileLoader("plexport", str(_REPO_ROOT / "plexport"))
_spec = importlib.util.spec_from_loader("plexport", _loader)
_module = importlib.util.module_from_spec(_spec)
sys.modules["plexport"] = _module
_loader.exec_module(_module)
