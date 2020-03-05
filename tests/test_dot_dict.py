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
from toolbox.logger import LogLevel, LoggerParams
from toolbox.dot_dict import DotDict, DictError


def test_resolution():
    """Test to make sure that resolution is properly handled"""
    unresolved = DotDict({
        "zero": {
            "one": {
                "two": {
                    "three":
                    4,
                    "four":
                    "${zero.one.two.three}",
                    "five":
                    "${zero.one.two.four}",
                    "six":
                    "six string",
                    "seven": [
                        "${zero.one.two.five}", {
                            "dict_in_list": "${zero.one.two.six}"
                        }
                    ]
                }
            }
        },
        "eight": "${zero.one.two.seven}"
    })
    resolved = DotDict({
        "zero": {
            "one": {
                "two": {
                    "three": 4,
                    "four": 4,
                    "five": 4,
                    "six": "six string",
                    "seven": [4, {
                        "dict_in_list": "six string"
                    }]
                }
            }
        },
        "eight": [4, {
            "dict_in_list": "six string"
        }]
    })
    attempt = unresolved.expand_and_resolve()
    print(attempt)
    assert (attempt == resolved.expand())


def test_circular_resolution():
    """Test to make sure that circular reference is handled"""
    unresolved = DotDict({
        "one.two": "${one.three}",
        "one": {
            "three": "${one.two}"
        }
    })
    with pytest.raises(DictError):
        unresolved.expand_and_resolve()


def test_nonexistent_resolution():
    """Test to make sure that nonexistent reference is handled"""
    unresolved = DotDict({"one.two": "${one.three}"})
    with pytest.raises(DictError):
        unresolved.expand_and_resolve()


def test_resolve_cat():
    """Test to make sure that circular reference is handled"""
    # Simple
    unresolved = DotDict({
        "one.two": "test",
        "one.five": "${one.four}",
        "one.four": "${one.two}",
        "one": {
            "three": "${one.four}"
        }
    })
    resolved = DotDict({
        "one": {
            "two": "test",
            "three": "test",
            "four": "test",
            "five": "test"
        }
    })
    unresolved.expand_and_resolve()
    print(unresolved)
    assert (unresolved == resolved)
    # Cat one string to another
    unresolved = DotDict({
        "one.two": "test",
        "one": {
            "three": "${one.two}_test"
        }
    })
    resolved = DotDict({"one": {"two": "test", "three": "test_test"}})
    attempt = unresolved.expand_and_resolve()
    print(attempt)
    assert (unresolved == resolved)
    # Cat two resolutions
    unresolved = DotDict({
        "one": "${two}/${three}",
        "two": "first",
        "three": "second"
    })
    resolved = DotDict({
        "one": "first/second",
        "two": "first",
        "three": "second"
    })
    attempt = unresolved.expand_and_resolve()
    print(attempt)
    assert (unresolved == resolved)


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
