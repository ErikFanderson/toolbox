#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/02/2020
"""Database for importing, expanding, and resolving configuration files"""

# Imports - standard library
from typing import Tuple, Any, Optional
import copy

# Imports - 3rd party packages

# Imports - local source
from .dot_dict import DotDict


class DatabaseError(Exception):
    """KeyError for internal database"""
    pass


class Database:
    """Database class for holding global toolbox database"""
    def __init__(self, protected_namespace: Optional[str] = None):
        self.internal = protected_namespace
        self._db = DotDict()

    def _load_dict(self, dictionary: dict) -> None:
        """Adds to internal database using a dict object
        :param dictionary Dict to be loaded into database
        WARNING! RUTHLESSLY OVERWRITES DATA
        """
        db = copy.deepcopy(dictionary)
        db = DotDict(db).flatten()
        for key, value in db.items():
            self._db.set_via_dot_string(key, value)

    def load_dict(self, dictionary: dict) -> None:
        """Adds to internal database using a dict object
        :param dictionary Dict to be loaded into database
        WARNING! RUTHLESSLY OVERWRITES DATA
        """
        db = copy.deepcopy(dictionary)
        db = DotDict(db).flatten()
        for key, value in db.items():
            if self.internal and key.startswith(self.internal):
                raise DatabaseError(
                    f'Key "{key}" attempts to modify protected namespace "{self.internal}"'
                )
            self._db.set_via_dot_string(key, value)

    def get_db(self, field: str) -> Tuple[bool, Any]:
        """Attempts to get value from database
        :param field Field to be retrieved from database
        :return Returns a tuple with success as first arg and requested
        value as second arg
        """
        try:
            return (True, copy.deepcopy(self._db.get_via_dot_string(field)))
        except KeyError:
            return (False, None)
