#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/29/2020
"""Docstring for module path_helper"""

# Imports - standard library
from typing import Tuple, Callable, Optional, List, Any, Union
from pathlib import Path
import sys
import subprocess
import getpass
from datetime import datetime

# Imports - 3rd party packages
import yaml
import yamale
from yamale.validators import DefaultValidators, Validator
from yamale.schema import Schema
from jinja2 import Environment, StrictUndefined, PackageLoader

# Imports - local source


def unlink_missing_ok(dirname: Path) -> None:
    ''' Unlinks directory if it exists '''
    try:
        (dirname).unlink()
    except FileNotFoundError:
        pass


def check_files(fnames: List[str],
                action: Optional[Callable[[str], Any]] = None
                ) -> Optional[List[Path]]:
    """Checks to see if files exist"""
    if fnames:
        checked_fnames = [check_file(fname, action) for fname in fnames]
        return_files = [fname for fname in checked_fnames if fname]
        if return_files:
            return return_files
    return []


def check_dirs(dirs: List[str], action: Optional[Callable[[str], Any]] = None
               ) -> Optional[List[Path]]:
    """Checks to see if dir exists"""
    if dirs:
        checked_dirs = [check_dir(directory, action) for directory in dirs]
        return_dirs = [directory for directory in checked_dirs if directory]
        if return_dirs:
            return return_dirs
    return []


def check_file(fname: str, action: Optional[Callable[[str], Any]] = None
               ) -> Optional[Path]:
    """Checks to see if file exists"""
    f = check_and_resolve(fname, files=True, dirs=False)
    if not f and action is not None:
        action(fname)
    return f


def check_dir(directory: str,
              action: Optional[Callable[[str], Any]] = None) -> Optional[Path]:
    """Checks to see if dir exists"""
    d = check_and_resolve(directory, files=False, dirs=True)
    if not d and action is not None:
        action(directory)
    return d


def check_and_resolve(rel_path: str, files: bool,
                      dirs: bool) -> Optional[Path]:
    '''Checks and resolves a single dir or file
    :param rel_paths List of relative paths to check
    :param files Checks to see if rel_path is a file
    :param dirs Checks to see whether rel_path is a directory
    :return Either a Path object or None
    '''
    if rel_path:
        rp = Path(rel_path).resolve()
        if files and rp.is_file():
            return rp
        elif dirs and rp.is_dir():
            return rp
    return None


class BinaryDriver:
    """Good mixin with tools to keep track of options and run binary files"""
    def __init__(self, binary: str):
        """Initialize with name of path to binary"""
        self.__binary = binary
        self.__options = []

    def add_option(self, value=None, flag=None):
        """Adds an option to the options list"""
        if value or flag:
            value = str(value).strip() if value else ''
            flag = str(flag).strip() if flag else ''
            self.__options.append(f"{flag} {value}".strip())

    def get_execute_string(self) -> str:
        """Returns the call to the executable"""
        options = ' '.join(self.__options)
        return f"{self.__binary} {options}"

    def execute(self, directory: str = None) -> str:
        """Actually executes"""
        return subprocess.run([self.__binary] + self.__options, cwd=directory)


class Anything(Validator):
    """ Custom anything validator """
    tag = 'anything'

    def _is_valid(self, value):
        return True


class Directory(Validator):
    """Validates something that is a valid directory
    Either pass as absolute path or will validate
    relative to the working directory
    """
    tag = 'dir'

    def _is_valid(self, value):
        if isinstance(value, str):
            return Path(value).is_dir()
        return False


class File(Validator):
    """Validates something that is a valid file
    Either pass as absolute path or will validate
    relative to the working directory
    """
    tag = 'file'

    def _is_valid(self, value):
        if isinstance(value, str):
            return Path(value).is_file()
        return False


class YamaleValidator:
    """Saves home directory and allows for easy checking of files
    Relies heavily on Pathlib
    """
    validators = DefaultValidators.copy()
    validators[Anything.tag] = Anything
    validators[File.tag] = File
    validators[Directory.tag] = Directory

    @classmethod
    def validate_files(cls,
                       yaml_fname: str,
                       schema_fname: str,
                       includes: dict = None) -> Union[str, dict]:
        """Uses yamale to calidate yaml file"""
        schema = yamale.make_schema(schema_fname, validators=cls.validators)
        if includes is not None:
            schema.add_include(includes)
        data = yamale.make_data(yaml_fname)
        try:
            yamale.validate(schema, data)
            return data[0][0]
        except ValueError as err:
            return str(err)

    @classmethod
    def validate_dicts(cls, data: dict, schema: dict,
                       includes: dict = None) -> Union[str, dict]:
        """Uses yamale to validate dictionary"""
        schema = Schema(schema, validators=cls.validators)
        if includes is not None:
            schema.add_include(includes)
        data = [(data, '')]
        try:
            yamale.validate(schema, data)
            return data[0][0]
        except ValueError as err:
            return str(err)

    @classmethod
    def validate_dict_with_file(cls,
                                data: dict,
                                schema_fname: str,
                                includes: dict = None) -> Union[str, dict]:
        """Uses yamale to validate dictionary"""
        schema = yamale.make_schema(schema_fname, validators=cls.validators)
        if includes is not None:
            schema.add_include(includes)
        data = [(data, '')]
        try:
            yamale.validate(schema, data)
            return data[0][0]
        except ValueError as err:
            return str(err)
