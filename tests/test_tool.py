#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module test_example"""

# Imports - standard library
from pathlib import Path

# Imports - 3rd party packages
import pytest

# Imports - local source
from toolbox.tool import ToolError
from toolbox.toolbox import ToolBox, ToolBoxParams
from toolbox.logger import LogLevel, LoggerParams
from toolbox.dot_dict import DotDict, DictError

MOCK_DIR = Path(__file__).resolve().parent / 'mock'


def test_tool_schema_include_invalid():
    args = ToolBoxParams(
        f'{MOCK_DIR}/schema_includes/tools.yml',
        build_dir='build',
        symlink=None,
        config=[f'{MOCK_DIR}/schema_includes/config_invalid.yml'],
        interactive=False,
        log_params=LoggerParams(LogLevel.DEBUG),
        job='example_job')
    tb = ToolBox(args)
    with pytest.raises(ToolError):
        tb.execute()


def test_tool_schema_include_valid():
    args = ToolBoxParams(
        f'{MOCK_DIR}/schema_includes/tools.yml',
        build_dir='build',
        symlink=None,
        config=[f'{MOCK_DIR}/schema_includes/config_valid.yml'],
        interactive=False,
        log_params=LoggerParams(LogLevel.DEBUG),
        job='example_job')
    tb = ToolBox(args)
    tb.execute()
