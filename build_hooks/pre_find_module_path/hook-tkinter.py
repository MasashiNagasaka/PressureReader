"""
Local override for PyInstaller pre-find hook.

The default hook excludes tkinter when Tcl/Tk probe fails in isolated mode.
In this project, tkinter import is valid at runtime, so we keep search_dirs
untouched and let module analysis include tkinter normally.
"""


def pre_find_module_path(hook_api):
    # Intentionally no-op: do not clear hook_api.search_dirs.
    return

