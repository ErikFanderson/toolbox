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


# TODO implement me
def test_additional_configs():
    """Checks to makes sure additional configs are loaded correctly"""
    # Check that configs are actually loaded
    # check to make sure that database is restored to original state after each task


# TODO implement me
def test_no_configs_passed():
    """Checks to makes sure works if no configs are passed"""


# TODO implement me
def test_tool_file_empty():
    """Checks to makes sure proper error raised when no tools found"""


# TODO implement me
def test_tool_is_not_class_tool():
    """Checks to makes sure that an imported tool is actually a Tool"""


# TODO implement me
def test_no_jobs_in_namespace():
    """Checks to makes sure that when no jobs namespace is passed an error occurs"""


# TODO implement me
def test_invalid_job_passed():
    """Checks to makes sure that invalid job names cause error"""


# TODO implement me
def test_valid_additional_config():
    """Checks that toolbox works when given valid
    additional configs when running a job.
    """


# TODO implement me
def test_invalid_additional_config():
    """Checks that toolbox errors when given invalid
    additional configs when running a job.
    """


# TODO implement me
def test_invalid_config_value():
    """Checks that toolbox errors when given invalid configs"""


# TODO implement me
def test_valid_config_value():
    """Checks that toolbox does not error when given valid configs"""


# TODO implement me
def test_missing_config_value():
    """Checks that toolbox errors when missing a required value"""


# TODO implement me
def test_tools_w_same_name_error():
    """Makes sure that all tools have different names"""


def test_invalid_config():
    """Test to make sure that invalid config files are properly ignored"""
    pass


def test_tool_validate():
    mock_dir = Path(__file__).resolve().parent / 'mock'
    args = ToolBoxParams(f'{mock_dir}/tools.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{mock_dir}/config_a.yml',
                             f'{mock_dir}/config_b.yml',
                             f'{mock_dir}/job.yml',
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_job')
    tb = ToolBox(args)
