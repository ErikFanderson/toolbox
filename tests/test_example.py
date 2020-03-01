#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module test_example"""

# Imports - standard library
from pathlib import Path

# Imports - 3rd party packages

# Imports - local source
from toolbox.toolbox import ToolBox, ToolBoxParams
from toolbox.path_helper import PathHelper
from toolbox.logger import LogLevel, LoggerParams


def test_path_helper():
    # Single checks
    f = PathHelper.check_file(__file__)
    print(f"File [True]: {f}")
    assert(f is not None)
    d = PathHelper.check_file(str(f.parent))
    print(f"Directory [False]: {d}")
    assert(d is None)
    f = PathHelper.check_dir(__file__)
    print(f"File [False]: {f}")
    assert(f is None)
    d = PathHelper.check_dir(str(PathHelper.check_file(__file__).parent))
    print(f"Directory [True]: {d}")
    assert(d is not None)
    # List checks
    f = PathHelper.check_files([__file__,__file__])
    print(f"Files [True]: {f}")
    assert(f is not None and len(f) == 2)
    d = PathHelper.check_files([str(f[0].parent),str(f[1].parent)])
    print(f"Directories [False]: {d}")
    assert(d is None)
    f = PathHelper.check_dirs([__file__,__file__])
    print(f"Files [False]: {f}")
    assert(f is None)
    f = PathHelper.check_files([__file__,__file__])
    d = PathHelper.check_dirs([str(f[0].parent),str(f[1].parent)])
    print(f"Directories [True]: {d}")
    assert(d is not None and len(d) == 2)

def test_tool_validate():
    mock_dir = Path(__file__).resolve().parent / 'mock'
    args = ToolBoxParams(f'{mock_dir}/tools.yml',
                        build_dir='test_build',
                        symlink=None,
                        config=[],
                        interactive=False,
                        log_params=LoggerParams(LogLevel.DEBUG),
                        job='test_job')
    tb = ToolBox(args)
