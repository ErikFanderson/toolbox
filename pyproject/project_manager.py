#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module project_manager"""

# Imports - standard library
from argparse import Namespace
from typing import Optional, NamedTuple, Any, List
from enum import Enum
from dataclasses import dataclass

# Imports - 3rd party packages

# Imports - local source

# TODO Use make_dataclass after reading all keys to dynamically create inputs database
# TODO There will be a separate outputs database that is generated and merged with inputs
# and spit out at the end of the job
# TODO Get resolution function working for reading in configs

class LogLevel(Enum):
    """Same logging levels used by python logging module"""
    DEBUG = 10 
    INFO = 20
    WARNING = 30 
    ERROR = 40
    CRITICAL = 50 

@dataclass(frozen=True)
class LoggerDb:
    """All necessary database parameters for creating a logger
    All parameters specified through global database (db should have defaults for some)
    """
    level: LogLevel
    out_fname: Optional[str]

class Logger:
    """Configurable logger for ProjectManager"""

    def __init__(self,p: LoggerDb) -> None:
        """Initializes a logger using db values from project manager"""
        self._logger = logging.getLogger() 

class ProjectManager:
    """Coordinates the running of tools and jobs"""

    def __init__(self, args: dict) -> None:
        """Inializes project manager with global namespace from args list"""
        self._db = self.generate_global_database(args)

    def get_db(self, field: str) -> Any:
        """Attempts to get value from database"""
        try:
            return self._db[field]
        except KeyError:
            pass # Use logger to issue warning

    def generate_global_database(self,args: dict) -> dict:
        """Generates global database from config files and args"""
        # Read in and combine all yml config and args
        #db["args"] = 
        #self._db["args"] = self.args
        #self.
        #self.add_args()
        print(args)
        #print(self._db)

    def combine_configs(configs: List[dict]):
        pass 

    def resolve_config(self):
        pass 

