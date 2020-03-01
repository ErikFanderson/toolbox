#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/29/2020
"""Docstring for module path_helper"""

# Imports - standard library
from typing import Tuple, Callable, Optional, List, Any, Union
from pathlib import Path
import json
import sys

# Imports - 3rd party packages
import yaml
import jsonschema

# Imports - local source
#from logger import LogLevel, Logger


class PathHelper:
    """Saves home directory and allows for easy checking of files
    Relies heavily on Pathlib
    """
    @staticmethod
    def validate_yaml(yaml_fname: str, schema_fname: str) -> Union[str, dict]:
        '''loads and validates yaml using schema fname
        :param yaml_fname Yaml filename for loading
        :param schema_fname JSON or YML filename for schema checking
        :return either loaded yaml dict or error message
        '''
        with open(schema_fname, 'r') as fp:
            loaded_schema = json.load(fp)
        with open(yaml_fname, 'r') as fp:
            loaded_yaml = yaml.load(fp, Loader=yaml.SafeLoader)
        try:
            jsonschema.validate(instance=loaded_yaml, schema=loaded_schema)
            return loaded_yaml
        except jsonschema.exceptions.ValidationError as err:
            return f'{err}\nYAML file "{yaml_fname}" does not conform to schema "{schema_fname}"'

    @staticmethod
    def get_rel_path(path):
        """Gets path relative to home_dir"""
        pass

    @classmethod
    def check_files(cls, fnames: List[str]) -> Optional[List[Path]]:
        """Checks to see if files exist"""
        return cls.check_and_resolve(fnames, files=True, dirs=False)

    @classmethod
    def check_dirs(cls, directories: List[str]) -> Optional[List[Path]]:
        """Checks to see if dir exists"""
        return cls.check_and_resolve(directories, files=False, dirs=True)

    @classmethod
    def check_file(cls, fname: str) -> Optional[Path]:
        """Checks to see if file exists"""
        return cls.check_and_resolve_single(fname, files=True, dirs=False)

    @classmethod
    def check_dir(cls, directory: str) -> Optional[Path]:
        """Checks to see if dir exists"""
        return cls.check_and_resolve_single(directory, files=False, dirs=True)

    @classmethod
    def check_and_resolve(cls, rel_paths: List[str], files: bool,
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
                rp = cls.check_and_resolve_single(path, files, dirs)
                if rp is not None:
                    resolved_paths.append(rp)
        if resolved_paths == []:
            return None
        else:
            return resolved_paths

    @classmethod
    def check_and_resolve_single(cls, rel_path: str, files: bool,
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
