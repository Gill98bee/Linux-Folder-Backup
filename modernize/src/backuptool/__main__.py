#!/usr/bin/env python3

"""Backuptool CLI entrypoint."""

from importlib.metadata import version

from .cli import app

if __name__ == "__main__":
    app()
