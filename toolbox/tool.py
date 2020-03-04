#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/02/2020
"""Docstring for module tool"""

# Imports - standard library
from abc import ABC, abstractmethod
from typing import List, Callable, Any
from pathlib import Path
import os

# Imports - 3rd party packages
from jinja2 import StrictUndefined, FileSystemLoader, Environment

# Imports - local source
from .database import Database
from .logger import LogLevel


class ToolError(Exception):
    """Error to show that tool implementation has hit exception"""


class Tool(ABC):
    """Base class that all tools must inherit from"""
    def __init__(self, db: Database, log: Callable[[str, LogLevel], None]):
        """Just sets the database"""
        self._db = db
        self._log = log
        self.path = self.get_db(f'internal.tools.{type(self).__name__}.path')

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
        with open(template_fname, 'r') as fp:
            fsl = FileSystemLoader(os.path.join(self.path, 'templates'))
            template = Environment(
                loader=fsl, undefined=StrictUndefined).from_string(fp.read())
        out = template.render(kwargs)
        with open(output_fname, 'w') as fp:
            fp.write(out)

    @abstractmethod
    def steps(self) -> List[Callable[[], None]]:
        """Main method that will run the steps"""
