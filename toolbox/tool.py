#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/02/2020
"""Docstring for module tool"""

# Imports - standard library
from abc import ABC, abstractmethod
from typing import List, Callable

# Imports - 3rd party packages

# Imports - local source
from .database import Database
from .logger import LogLevel


class Tool(ABC):
    """Base class that all tools must inherit from"""
    def __init__(self, db: Database, log: Callable[[str, LogLevel], None]):
        """Just sets the database"""
        self._db = db
        self._log = log

    def set_log_fn(self, log: Callable[[str, LogLevel], None]):
        """For changing the logging functionality between steps"""
        self._log = log

    def log(self, msg: str, level: Callable[[str, LogLevel], None]):
        """Function for logging information"""
        self._log(msg, level)

    @abstractmethod
    def steps(self) -> List[Callable[[], None]]:
        """Main method that will run the steps"""
