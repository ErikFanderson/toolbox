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
from toolbox.dot_dict import DotDict

def test_dot_dict():
    # Flatten first
    my_dict = DotDict({
        "zero": {"one": {"two": {"three": 4}}},
        "zero.one.two": 0,
        "zero.one.four": {"five.six": "test_str"}
    })
    flattened_dict = DotDict({
        "zero.one.two.three": 4,
        "zero.one.two": 0,
        "zero.one.four.five.six": "test_str"
    })
    target_dict = DotDict({
        "zero": {"one": {"two": 0, "four": {"five": {"six": "test_str"}}}},
    })
    my_dict.flatten()
    assert(my_dict == flattened_dict)
    # Dot expand second
    my_dict.dot_expand()
    print(my_dict)
    assert(my_dict == target_dict)
    assert(False)


def test_dot_dict_expand():
    """Tests the very important expand function for my dot_dict"""
    pass
    #my_dict = DotDict({"test1":{"test2": {"test3.test8":  69,"test4": "fuck"}}})
    #print(my_dict.flatten())
    #my_dict = DotDict({"test1":{}})
    #print(my_dict.flatten())
    #my_dict = DotDict({"test1.test2":10})
    #print(my_dict.flatten())

def test_circular_resolution():
    """Test to make sure that circular reference is handled"""
    pass

def test_invalid_config():
    """Test to make sure that invalid config files are properly ignored"""
    pass

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
