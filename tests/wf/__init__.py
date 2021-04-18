import sys
from inspect import getsourcefile
from os.path import abspath
from pathlib import Path

thispath = abspath(getsourcefile(lambda: 0))
root_path = Path(thispath).parent.parent.parent.parent
sys.path.insert(0, str(root_path))
