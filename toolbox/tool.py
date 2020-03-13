#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/02/2020
"""Docstring for module tool"""

# Imports - standard library
import os
from abc import ABC, abstractmethod
from typing import List, Callable, Any, Optional
from pathlib import Path
import getpass
from datetime import datetime

# Imports - 3rd party packages
from jinja2 import StrictUndefined, FileSystemLoader, Environment

# Imports - local source
from .database import Database
from .logger import LogLevel, HasLogFunction
from .utils import YamaleValidator


class ToolError(Exception):
    """Error to show that tool implementation has hit exception"""


class Tool(HasLogFunction, ABC):
    """Base class that all tools must inherit from
    Inherits from HasLogFunction which is also an abstract class
    """
    def __init__(self, db: Database, log: Callable[[str, LogLevel], None]):
        """Just sets the database"""
        self._db = db
        self._log = log
        self.path = self.get_db(f'internal.tools.{type(self).__name__}.path')
        self.check_db()

    def check_db(self):
        """Checks database against default and provided schemas
        To be run after loading tools, configs, and performing resolution
        # TODO ultimately this should be rewritten to not perform validation
        serially... Construct large schema and run on entire database
        """
        # Check tool and all tool superclasses
        for c in type(self).mro():
            if issubclass(c, Tool) and not c == Tool:
                self.check_db_tool(c.__name__)
                add_sch = self.get_db(
                    f"internal.tools.{c.__name__}.additional_schemas")
                for schema in add_sch:
                    self.check_db_tool(schema)

    def get_additional_schemas(self, tool_name: str):
        """Gets all schema names associated with this tool"""
        return []

    def check_db_tool(self, tool_name: str):
        """Checks the database and makes sure it has proper values for the given tool"""
        # Check tool properties
        tool = self.get_db(f"internal.tools.{tool_name}")
        for prop_name, prop in tool['properties'].items():
            dot_str = f"tools.{tool_name}.{prop_name}"
            data = {f"{prop_name}": self.get_db(dot_str)}
            schema = {f"{prop_name}": prop["schema"]}
            includes = None
            if "schema_includes" in list(tool.keys()):
                includes = tool["schema_includes"]
            err_msg = YamaleValidator.validate_dicts(data, schema, includes)
            if isinstance(err_msg, str):
                descr = prop["description"]
                raise ToolError(
                    f'Invalid value for property "{dot_str}".\nDescription: {descr}{err_msg}'
                )

    def set_log_fn(self, log: Callable[[str, LogLevel], None]):
        """For changing the logging functionality between steps"""
        self._log = log

    def log(self, msg: str, level: LogLevel = LogLevel.INFO) -> None:
        """Function for logging information"""
        self._log(msg, level)

    def get_db(self, dot_str: str):
        """Allows for accessing database w/o touching _db
        :param dot_str Dot string for accessing database (key1.key2 etc...)
        """
        return self._db.get_db(dot_str)

    @abstractmethod
    def steps(self) -> List[Callable[[], None]]:
        """Main method that will run the steps"""
