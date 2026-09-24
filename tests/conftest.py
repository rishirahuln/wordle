"""conftest.py — make the parent 'wordle/' directory importable in tests."""

import os
import sys

# Add the project root (wordle/) to sys.path so tests can import game, history, etc.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
