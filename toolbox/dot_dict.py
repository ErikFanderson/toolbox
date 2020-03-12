#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/01/2020
"""Docstring for module dot_dict"""

# Imports - standard library
from typing import Tuple, Optional, NamedTuple, Any, Callable, List
from typing import Pattern
import copy
import sys
import re

# Imports - 3rd party packages

# Imports - local source


class DictError(Exception):
    """For errors involving the custom DotDict class"""
    pass


class DotDict(dict):
    def set_via_dot_string(self, dot_str: str, value: Any) -> bool:
        """Returns a modified dictionary accessed by a dot access_via_string
        Will unapologetically redefine values! Need to allow for adding to dictionaries!
        :param dot_str Dot string such as key1.key2.key3
        :param value The value at the end of the key string
        """
        keys = dot_str.split('.')
        set_val = self
        for i, k in enumerate(keys):
            if len(keys) == (i + 1):
                try:
                    set_val[k] = value
                except TypeError:
                    raise DictError(
                        f"Illegal redefinition of global database field.")
            else:
                try:
                    set_val = set_val[k]
                except KeyError:
                    set_val[k] = {}
                    set_val = set_val[k]
                except TypeError:
                    raise DictError(
                        f"Illegal redefinition of global database field.")

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

    def expand_and_resolve(self) -> dict:
        """Attempts to flatten, resolve, and then expand dictionary"""
        self.flatten()
        self.dot_expand()
        self.resolve()
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

    def resolve(self):
        """Runs resolve item on itself"""
        try:
            self.resolve_item(self, re.compile(r"\${([a-zA-Z0-9\._]+)}"))
        except RecursionError:
            raise DictError("""Maximum recursion depth reached.
There is most likely a circular reference present""")

    def resolve_item(self, item: Any, regex: Pattern) -> Any:
        """If values are dot string keys then tries to resolve dot strings
        :param item Item to be resolved.
        :param regex Regular expression to be used to find variables to resolve
        :return Returns the resolved item
        TODO make it okay to concatenate objects as long as they have same type?
        TODO Add in circular reference check
        TODO May need to update regex passed in from resolve... Might need
        some up front checks on the keys passed to toolbox to make sure
        only valid characters are used.
        """
        # Perform resolution
        if isinstance(item, str):
            # Check for Match
            matches = regex.findall(item)
            if matches:
                res_items = []
                try:
                    for match in matches:
                        r = self.resolve_item(self.get_via_dot_string(match),
                                              regex)
                        res_items.append(r)
                except KeyError:
                    raise DictError(f'Item "{match}" not found.')
                # Check that they are all strings if there are multiple matches
                if len(res_items) > 1:
                    for res in res_items:
                        if not isinstance(res, str):
                            raise DictError("Can only concatenate strings!")
                        item = regex.sub(res, item, 1)
                # If a single item then just resolve it
                elif len(res_items) == 1:
                    if isinstance(res_items[0], dict) or isinstance(
                            res_items[0], list):
                        item = self.resolve_item(res_items[0], regex)
                    elif isinstance(res_items[0], str):
                        item = regex.sub(res_items[0], item, 1)
                    else:
                        item = res_items[0]
        elif isinstance(item, list):
            for i, element in enumerate(item):
                item[i] = self.resolve_item(element, regex)
        elif isinstance(item, dict):
            for key, value in item.items():
                item[key] = self.resolve_item(value, regex)
        return item
