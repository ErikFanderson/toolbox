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


# TODO implement me
def test_protected_namespace_database():
    """Checks protected namespace cannot be overwritten in database"""
