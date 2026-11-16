import importlib, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import synth
for m in sys.argv[1:]:
    synth(importlib.import_module(m).LINES.values())
