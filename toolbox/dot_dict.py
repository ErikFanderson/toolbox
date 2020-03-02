#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/01/2020
"""Docstring for module dot_dict"""

# Imports - standard library
from typing import Tuple, Optional, NamedTuple, Any, Callable, List
import copy
import sys

# Imports - 3rd party packages

# Imports - local source


class DictError(Exception):
    """For errors involving the custom DotDict class"""
    pass


class DotDict(dict):
    def set_via_dot_string(self, dot_str: str, value: Any) -> bool:
        """Returns a modified dictionary accessed by a dot access_via_string
        Will unapologetically redefine values!
        :param dot_str Dot string such as key1.key2.key3
        :param value The value at the end of the key string
        """
        keys = dot_str.split('.')
        set_val = self
        for i, k in enumerate(keys):
            try:
                set_val = set_val[k]
            except KeyError:
                if len(keys) == (i + 1):
                    set_val[k] = value
                else:
                    set_val[k] = {}
                    set_val = set_val[k]
            except TypeError:
                raise DictError(
                    "Illegal redefinition of global database field.")

    def get_via_dot_string(self, dot_str: str) -> Any:
        """Allows for accessing dictionary via dot methods"""
        keys = dot_str.split('.')
        return self.get_via_list(keys)

    def get_via_list(self, keys: List[str]) -> Any:
        """Allows for accessing dictionary via list of strings"""
        return_val = self
        for i, k in enumerate(keys):
            return_val = return_val[k]
        return return_val

    @staticmethod
    def flatten_recursive(db: dict, prefix: str = '',
                          keys: list = []) -> Tuple[str, Any]:
        """Returns first dot key value found"""
        for key, value in db.items():
            new_prefix = prefix + '.' + key if prefix else key
            if isinstance(value, dict) and value != {}:
                return DotDict.flatten_recursive(value, new_prefix,
                                                 keys + [key])
            else:
                return (new_prefix, value, keys + [key])

    def delete_key(self, keys: List[str]) -> dict:
        """Iteratively deletes keys in dictionary using a list of keys"""
        if len(keys) > 1:
            for j in reversed(range(len(keys))):
                del_dict = self.get_via_list(keys[:j])
                del_key = keys[j]
                if j == len(keys) - 1 or del_dict[del_key] == {}:
                    del del_dict[del_key]
        elif len(keys) == 1:
            del self[keys[0]]
        return self

    def expand(self) -> dict:
        """Attempts to flatten and then expand dictionary
        to allow for dot notation namespace definition
        """
        self.flatten()
        self.dot_expand()
        return self

    def dot_expand(self):
        """Does a single layer expansion assuming dictionary is flat"""
        for key, value in sorted(self.items()):
            del self[key]
            self.set_via_dot_string(key, value)
        return self

    def flatten(self) -> dict:
        flat_dict = DotDict()
        while self != {}:
            flat_key, value, old_keys = DotDict.flatten_recursive(self)
            self.delete_key(old_keys)
            flat_dict[flat_key] = value
        self.update(flat_dict)
        return self
