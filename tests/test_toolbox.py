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
from toolbox.tool import ToolError
from toolbox.toolbox import ToolBoxError

MOCK_DIR = Path(__file__).resolve().parent / 'mock'


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
def test_tools_w_same_name_error():
    """Makes sure that all tools have different names"""


def test_missing_superclass_property_tool_inheritance():
    """Make sure that tools are check correctly"""
    args = ToolBoxParams(f'{MOCK_DIR}/tool_inheritance/tool_subclass/tools_subclass.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_b.yml',
                             f'{MOCK_DIR}/tool_inheritance/tool_subclass/config_subclass.yml',
                             f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_subclass_job')
    tb = ToolBox(args)
    with pytest.raises(ToolError):
        tb.execute()


def test_missing_subclass_property_tool_inheritance():
    """Test subclass of tool w/ missing subclass property"""
    args = ToolBoxParams(f'{MOCK_DIR}/tool_inheritance/tool_subclass/tools_subclass.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_a.yml',
                             f'{MOCK_DIR}/basic/config_b.yml', f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_subclass_job')
    tb = ToolBox(args)
    with pytest.raises(ToolError):
        tb.execute()


def test_successful_tool_inheritance():
    """Make sure that tools are check correctly"""
    args = ToolBoxParams(f'{MOCK_DIR}/tool_inheritance/tool_subclass/tools_subclass.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_a.yml',
                             f'{MOCK_DIR}/basic/config_b.yml',
                             f'{MOCK_DIR}/tool_inheritance/tool_subclass/config_subclass.yml',
                             f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_subclass_job')
    tb = ToolBox(args)
    tb.execute()


def test_invalid_tools_file():
    """Tests to make sure that assertion is raised when invalid tool property is loaded"""
    args = ToolBoxParams(f'{MOCK_DIR}/basic/tools_invalid.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_a.yml',
                             f'{MOCK_DIR}/basic/config_b.yml', f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_job')
    with pytest.raises(ToolBoxError):
        tb = ToolBox(args)


def test_missing_tools_file():
    """Tests to make sure that assertion is raised when invalid tool property is loaded"""
    args = ToolBoxParams(f'{MOCK_DIR}/nonexistent.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_a.yml',
                             f'{MOCK_DIR}/basic/config_b.yml', f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_job')
    with pytest.raises(ToolBoxError):
        tb = ToolBox(args)


def test_invalid_job():
    """Tests to make sure that assertion is raised when invalid tool property is loaded"""
    args = ToolBoxParams(f'{MOCK_DIR}/basic/tools.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_a.yml',
                             f'{MOCK_DIR}/basic/config_b.yml',
                             f'{MOCK_DIR}/basic/job_invalid.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_job')
    with pytest.raises(ToolBoxError):
        tb = ToolBox(args)


def test_invalid_tool_properties():
    """Tests to make sure that assertion is raised when invalid tool property is loaded"""
    args = ToolBoxParams(f'{MOCK_DIR}/basic/tools.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_a_invalid.yml',
                             f'{MOCK_DIR}/basic/config_b.yml', f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_job')
    tb = ToolBox(args)
    with pytest.raises(ToolError):
        tb.execute()


#def test_invalid_config_file_path
def test_missing_tool_properties():
    """Tests to make sure that assertion is raised when missing a tool property"""
    args = ToolBoxParams(f'{MOCK_DIR}/basic/tools.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/nonexistent.yml',
                             f'{MOCK_DIR}/basic/config_b.yml', f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_job')
    tb = ToolBox(args)
    with pytest.raises(ToolError):
        tb.execute()


def test_tool_validate():
    args = ToolBoxParams(f'{MOCK_DIR}/basic/tools.yml',
                         build_dir='build',
                         symlink=None,
                         config=[
                             f'{MOCK_DIR}/basic/config_a.yml',
                             f'{MOCK_DIR}/basic/config_b.yml', f'{MOCK_DIR}/basic/job.yml'
                         ],
                         interactive=False,
                         log_params=LoggerParams(LogLevel.DEBUG),
                         job='example_job')
    tb = ToolBox(args)
    tb.execute()
