#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/01/2020
"""Docstring for module dot_dict"""

# Imports - standard library
from typing import Tuple, Optional, NamedTuple, Any, Callable, List
import copy

# Imports - 3rd party packages

# Imports - local source

class DotDict(dict):

    def set_via_dot_string(self, dot_str: str,value: Any) -> None:
        """Returns a modified dictionary accessed by a dot access_via_string
        :param dot_str Dot string such as key1.key2.key3
        :param value The value at the end of the key string
        """
        keys = dot_str.split('.')
        set_val = self
        for i,k in enumerate(keys):
            try:
                set_val = set_val[k]
            except KeyError:
                if len(keys) == (i+1):
                    set_val[k] = value
                else:
                    set_val[k] = {}
                    set_val = set_val[k]
        set_val = value

    def get_via_dot_string(self, dot_str: str) -> Any:
        """Allows for accessing dictionary via dot methods"""
        keys = dot_str.split('.')
        return_val = self
        for i,k in enumerate(keys):
            return_val = return_val[k]
        return return_val

    @staticmethod
    def flatten_recursive(db: dict,prefix: str = '',keys: list = []) -> Tuple[str,Any]:
        for key,value in db.items():
            new_prefix = prefix + '.' + key if prefix else key
            if isinstance(value,dict) and value != {}:
                return DotDict.flatten_recursive(value,new_prefix,keys + [key])
            else:
                return (new_prefix,value,keys + [key])

    @staticmethod
    def delete_key(db: dict,keys: List[str]) -> dict:
        db_copy = copy.deepcopy(db)
        set_val = db_copy
        for i,k in enumerate(keys):
            if i+1 == len(keys):
                del set_val[k]
            else:
                set_val = set_val[k]
        return db_copy

    def expand(self) -> Tuple[str,Any]:
        new_dict = DotDict()
        while self != {}:
            flat_key, value, old_keys = DotDict.flatten_recursive(self)
            self = DotDict.delete_key(self,old_keys)
            new_dict.set_via_dot_string(flat_key,value)
        self.update(new_dict)
        return self
