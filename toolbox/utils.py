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
    return None


def check_dirs(dirs: List[str], action: Optional[Callable[[str], Any]] = None
               ) -> Optional[List[Path]]:
    """Checks to see if dir exists"""
    if dirs:
        checked_dirs = [check_dir(directory, action) for directory in dirs]
        return_dirs = [directory for directory in checked_dirs if directory]
        if return_dirs:
            return return_dirs
    return None


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


class JinjaModule:
    """Base jinja module w/ render function"""

    #def __init__(self, search_dirs: List[str], environment: Optional[Environment] = None):
    def __init__(self, environment: Environment):
        """Creates a jinja2 environment for this module
        :param package The package that this module resides in
        :param templates The path to the templates dir relative to the package
        """
        self.env = environment

    def render_to_file(self, template: str, outfile: str, **kwargs: Any):
        """Gets template from environment and renders
        :param template template to be used
        :param outfile Name/path of output file
        :param kwargs Key word arguments to be passed to jinja2 template
        """
        with open(outfile, 'w') as fp:
            fp.write(self.render(template, **kwargs))

    def render(self, template: str, **kwargs: Any):
        """Gets template from environment and renders
        :param template template to be used
        :param outfile Name/path of output file
        """
        # Defaults
        kwargs.update({"_tab": 4 * ' '})
        # Always pass username and date
        uname = getpass.getuser()
        date = datetime.now().strftime("%m/%d/%Y-%H:%M:%S")
        template = self.env.get_template(template)
        return template.render(**kwargs, _uname=uname, _date=date)
