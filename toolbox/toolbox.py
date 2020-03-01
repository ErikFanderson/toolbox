#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module project_manager"""

# Imports - standard library
from argparse import Namespace
from typing import Optional, NamedTuple, Any, Callable, List
from enum import Enum
from dataclasses import dataclass
import os, sys
from pathlib import Path

# Imports - 3rd party packages

# Imports - local source
#from cli_driver import CLIArgs
from logger import Logger, LogLevel, LoggerParams
from path_helper import PathHelper

# TODO Use make_dataclass after reading all keys to dynamically create inputs database
# TODO There will be a separate outputs database that is generated and merged with inputs
# and spit out at the end of the job
# TODO Get resolution function working for reading in configs


@dataclass(frozen=True)
class ToolBoxParams:
    """All command line args to create ToolBox"""
    tool_file: str
    build_dir: str
    symlink: str
    config: List[str]
    interactive: bool
    log_level: LogLevel


class ToolBox:
    """Coordinates the running of tools and jobs"""
    def __init__(self, args: ToolBoxParams) -> None:
        """Inializes project manager with global namespace from args list"""
        # Set private and public members
        self._logger = Logger(LoggerParams(level=args.log_level))
        self.log = self._logger.log
        # Ensure that home directory is set
        self._home_dir = PathHelper.check_dir(os.getenv('TOOLBOX_HOME'))
        if self._home_dir is None:
            self.exit('TOOLBOX_HOME variable not set or incorrectly set.')
        # Populate Database
        self._db = self.generate_global_database(args)

    def check_file(self, fname: str) -> Optional[Path]:
        """Checks a single file"""
        checked_file = PathHelper.check_file(fname)
        if checked_file is None:
            self.log(f'"{fname}" is not a valid file.', LogLevel.WARNING)
        return checked_file

    def check_dir(self, directory: str) -> Optional[Path]:
        """Checks a single directory"""
        checked_dir = PathHelper.check_dir(directory)
        if checked_dir is None:
            self.log(f'"{directory}" is not a valid directory.',
                     LogLevel.WARNING)
        return checked_dir

    def check_files(self, fnames: List[str]) -> Optional[List[Path]]:
        """Check files function but with added logging"""
        checked_fnames = [self.check_file(fname) for fname in fnames]
        return [fname for fname in checked_fnames if fname]

    def check_dirs(self, dirs: List[str]) -> Optional[List[Path]]:
        """Check files function but with added logging"""
        checked_dirs = [self.check_dir(directory) for directory in dirs]
        return [directory for directory in checked_dirs if directory]

    def exit(self, msg: str) -> None:
        """Method for nicely erroring and exiting"""
        self.log(msg, LogLevel.ERROR)
        sys.exit(-1)

    def get_db(self, field: str) -> Any:
        """Attempts to get value from database"""
        try:
            return self._db[field]
        except KeyError:
            pass  # Use logger to issue warning

    def generate_global_database(self, args: ToolBoxParams) -> dict:
        """Generates global database from config files and args"""
        tool_paths = self.validate_tool_file(args.tool_file)
        # Iterate through tools
        # Load default tool config
        #
        # Iterate through config files
        # Overwrites any default settings
        # combine_configs
        # combine_schemas
        # check_configs
        # return make_dataclass
        #configs = args['config']
        #self.combine_configs()

    def validate_tool_file(self, fname: str) -> List[Path]:
        """Validates the tool file
        :param fname Filename of the tool file
        :return List of Paths to tools
        """
        # Load tools file (may include globals)
        tool_file = self.check_file(fname)
        if tool_file is None:
            self.exit('Cannot find tool file "{args.tool_file}"')
        test = self.check_file("toolboxma.json")
        schema_file = self.check_file(
            str(self._home_dir / "toolbox/schema.json"))
        # Validate tool config
        tool_config = PathHelper.validate_yaml(tool_file, schema_file)
        if isinstance(tool_config, str):
            self.exit(tool_config)
        # Exit if no valid tools found
        tool_paths = self.check_dirs(tool_config['tools'])
        if tool_paths == []:
            self.exit(f'No valid tools found in "{tool_file}"')
        return tool_paths

    def validate_tools(self):
        pass

    def validate_tool(self):
        pass

    def combine_configs(self, configs: List[dict]) -> str:
        """Generates global config string/namespace"""
        pass

    def combine_schemas(self, configs: List[dict]) -> str:
        """Generates global schema file/namespace"""
        pass

    def check_configs(self, configs: List[dict]) -> None:
        """Checks global namespace against global schemaspace"""
        pass

    def resolve_config(self):
        pass

    def execute(self):
        pass
