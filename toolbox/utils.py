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

# Imports - 3rd party packages
import yaml
import yamale
from yamale.validators import DefaultValidators, Validator
from yamale.schema import Schema

# Imports - local source


def unlink_missing_ok(dirname: Path) -> None:
    ''' Unlinks directory if it exists '''
    try:
        (dirname).unlink()
    except FileNotFoundError:
        pass


def check_files(fnames: List[str]) -> Optional[List[Path]]:
    """Checks to see if files exist"""
    return check_and_resolve(fnames, files=True, dirs=False)


def check_dirs(directories: List[str]) -> Optional[List[Path]]:
    """Checks to see if dir exists"""
    return check_and_resolve(directories, files=False, dirs=True)


def check_file(fname: str) -> Optional[Path]:
    """Checks to see if file exists"""
    return check_and_resolve_single(fname, files=True, dirs=False)


def check_dir(directory: str) -> Optional[Path]:
    """Checks to see if dir exists"""
    return check_and_resolve_single(directory, files=False, dirs=True)


def check_and_resolve(rel_paths: List[str], files: bool,
                      dirs: bool) -> Optional[List[Path]]:
    '''Checks and resolves a list of dirs, files, or files and dirs
    :param rel_paths List of relative paths to check
    :param files Checks to see if rel_path is a file
    :param dirs Checks to see whether rel_path is a directory
    :return Either a list of Path objects or None
    '''
    if rel_paths:
        resolved_paths = []
        for i, path in enumerate(rel_paths):
            rp = check_and_resolve_single(path, files, dirs)
            if rp is not None:
                resolved_paths.append(rp)
    if resolved_paths == []:
        return None
    else:
        return resolved_paths


def check_and_resolve_single(rel_path: str, files: bool,
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

    def execute(self) -> str:
        """Actually executes"""
        return subprocess.run([self.__binary] + self.__options)


class Anything(Validator):
    """ Custom anything validator """
    tag = 'anything'

    def _is_valid(self, value):
        return True


class Validator:
    """Saves home directory and allows for easy checking of files
    Relies heavily on Pathlib
    """
    validators = DefaultValidators.copy()
    validators[Anything.tag] = Anything

    @classmethod
    def yamale_validate_files(cls, yaml_fname: str,
                              schema_fname: str) -> Union[str, dict]:
        """Uses yamale to calidate yaml file"""
        schema = yamale.make_schema(schema_fname, validators=cls.validators)
        data = yamale.make_data(yaml_fname)
        try:
            yamale.validate(schema, data)
            return data[0][0]
        except ValueError as err:
            return str(err)

    @classmethod
    def yamale_validate_dicts(cls, data: dict,
                              schema: dict) -> Union[str, dict]:
        """Uses yamale to validate dictionary"""
        schema = Schema(schema, validators=cls.validators)
        data = [(data, '')]
        try:
            yamale.validate(schema, data)
            return data[0][0]
        except ValueError as err:
            return str(err)

    @classmethod
    def yamale_validate_dict_with_file(cls, data: dict,
                                       schema_fname: str) -> Union[str, dict]:
        """Uses yamale to validate dictionary"""
        schema = yamale.make_schema(schema_fname, validators=cls.validators)
        data = [(data, '')]
        try:
            yamale.validate(schema, data)
            return data[0][0]
        except ValueError as err:
            return str(err)
