#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/02/2020
"""Database for importing, expanding, and resolving configuration files"""

# Imports - standard library
from typing import Tuple, Any

# Imports - 3rd party packages

# Imports - local source
from .dot_dict import DotDict


class Database:
    """Database class for holding global toolbox database"""
    def __init__(self):
        self._db = DotDict()

    def load_dict(self, dictionary: dict) -> None:
        """Adds to internal database using a dict object
        :param dictionary Dict to be loaded into database
        """
    def load_yml(self, fname: str) -> None:
        """Adds to internal database using yaml files
        :param fname filename for the yaml config file
        """
    def get_db(self, field: str) -> Tuple[bool, Any]:
        """Attempts to get value from database
        :param field Field to be retrieved from database
        :return Returns a tuple with success as first arg and requested
        value as second arg
        """
        try:
            return (True, self._db[field])
        except KeyError:
            return (False, None)
