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
from toolbox.toolbox import ToolBox, ToolBoxParams
from toolbox.path_helper import PathHelper
from toolbox.logger import LogLevel, LoggerParams
from toolbox.dot_dict import DotDict, DictError


def test_circular_resolution():
    """Test to make sure that circular reference is handled"""
    pass


def test_dot_dict_redefinition():
    """Fails becuase tries to redefine field"""
    # Flatten first
    my_dict = DotDict({
        "zero": {
            "one": {
                "two": {
                    "three": 4
                }
            }
        },
        "zero.one.two": 0,
        "zero.one.four": {
            "five.six": "test_str"
        }
    })
    flattened_dict = DotDict({
        "zero.one.two.three": 4,
        "zero.one.two": 0,
        "zero.one.four.five.six": "test_str"
    })
    # Flatten should work
    my_dict.flatten()
    assert (my_dict == flattened_dict)
    # Redefinition error should be raised
    with pytest.raises(DictError):
        my_dict.dot_expand()


def test_dot_dict_expand():
    """Should successfully expand dictionary"""
    # Flatten first
    my_dict = DotDict({
        "zero": {
            "one": {
                "two": {
                    "three": 4
                }
            }
        },
        "zero.one.four": {
            "five.six": "test_str"
        },
        "test.test.hello": ["list", "of", "things"]
    })
    target_dict = DotDict({
        "zero": {
            "one": {
                "two": {
                    "three": 4
                },
                "four": {
                    "five": {
                        "six": "test_str"
                    }
                }
            }
        },
        "test": {
            "test": {
                "hello": ["list", "of", "things"]
            }
        }
    })
    assert (my_dict.expand() == target_dict)
