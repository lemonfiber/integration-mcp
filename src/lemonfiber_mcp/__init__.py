# Copyright (c) 2026 NightWorksIO
"""lemonfiber for AI assistants: a Model Context Protocol server reaching a stack through an integration key.

The stack is reached only through the vendored sdk-python, whose own imports
name it `lemonfiber`, so its directory is put on the import path before anything
here imports it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_vendor"))
