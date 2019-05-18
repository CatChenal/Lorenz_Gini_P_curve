import os
import sys

import numpy as np
import pandas as pd
pd.set_option("display.max_colwidth", 200)

from pprint import pprint as pp
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

print('Python: {}\n'.format(sys.version))
print('Currrent dir:', os.path.abspath(os.path.curdir))

def add_to_sys_path(this_path, up=False):
    """
    Prepend this_path to sys.path.
    If up=True, path refers to parent folder (1 level up).
    """
    for p in sys.path:
        p = os.path.abspath(p)
    if up:
        newp = os.path.abspath(os.path.join(this_path, '..'))
    else:
        newp = os.path.abspath(this_path)
        
    if this_path not in (p, p + os.sep):
        print('Path added to sys.path: {}'.format(newp))
        sys.path.insert(0, newp)
        
# if notebook inside another folder, eg ./notebooks:
up =  os.path.abspath(os.path.curdir).endswith('notebooks')
add_to_sys_path(os.path.curdir, up)


def is_lab_notebook():
    import re
    import psutil
        
    return any(re.search('jupyter-lab-script', x)
               for x in psutil.Process().parent().cmdline())

if is_lab_notebook():
    # need to use Markdown if referencing variables:
    from IPython.display import Markdown, HTML
    msg = "This is a JupyterLab notebook: Use `IPython.display.\
           Markdown()` if referencing variables in a Markdown cell."
    return Markdown('### {}'.format(msg))

%load_ext autoreload
%autoreload 2
