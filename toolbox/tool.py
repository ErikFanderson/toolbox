#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/02/2020
"""Docstring for module tool"""

# Imports - standard library
import os
from abc import ABC, abstractmethod
from typing import List, Callable, Any
from pathlib import Path
import getpass
from datetime import datetime

# Imports - 3rd party packages
from jinja2 import StrictUndefined, FileSystemLoader, Environment

# Imports - local source
from .database import Database
from .logger import LogLevel
from .utils import Validator


class ToolError(Exception):
    """Error to show that tool implementation has hit exception"""


class Tool(ABC):
    """Base class that all tools must inherit from"""
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

    def check_db_tool(self, tool_name: str):
        """Checks the database and makes sure it has proper values for the given tool"""
        # Check tool properties
        tool = self.get_db(f"internal.tools.{tool_name}")
        for prop_name, prop in tool['properties'].items():
            dot_str = f"tools.{tool_name}.{prop_name}"
            data = {f"{prop_name}": self.get_db(dot_str)}
            schema = {f"{prop_name}": prop["schema"]}
            err_msg = Validator.yamale_validate_dicts(data, schema)
            if isinstance(err_msg, str):
                descr = prop["description"]
                raise ToolError(
                    f'Invalid value for property "{dot_str}".\nDescription: {descr}{err_msg}'
                )

    def set_log_fn(self, log: Callable[[str, LogLevel], None]):
        """For changing the logging functionality between steps"""
        self._log = log

    def log(self, msg: str, level: LogLevel = LogLevel.INFO):
        """Function for logging information"""
        self._log(msg, level)

    def get_db(self, dot_str: str):
        """Allows for accessing database w/o touching _db
        :param dot_str Dot string for accessing database (key1.key2 etc...)
        """
        return self._db.get_db(dot_str)

    def jinja_render(self, template_fname: str, output_fname: str,
                     **kwargs: Any):
        '''Loads template and outputs to file
        :param template_fname filename of jinja template
        :param output_fname filename of output file
        '''
        # Load any additional template directories
        dirs = [os.path.join(self.path, 'templates')]
        if 'additional_template_dirs' in kwargs:
            dirs += kwargs['additional_template_dirs']
            del kwargs['additional_template_dirs']
        # Open template and read
        with open(template_fname, 'r') as fp:
            fsl = FileSystemLoader(dirs)
            template = Environment(
                loader=fsl, undefined=StrictUndefined).from_string(fp.read())
        # Render template and output to file
        uname = getpass.getuser()
        date = datetime.now().strftime("%m/%d/%Y-%H:%M:%S")
        out = template.render(kwargs, uname=uname, date=date)
        with open(output_fname, 'w') as fp:
            fp.write(out)

    @abstractmethod
    def steps(self) -> List[Callable[[], None]]:
        """Main method that will run the steps"""
