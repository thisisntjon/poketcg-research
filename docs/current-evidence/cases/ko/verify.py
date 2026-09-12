#!/usr/bin/env python3
"""Portable archive entry point for the KO case."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("verify_case.py")), run_name="__main__")
