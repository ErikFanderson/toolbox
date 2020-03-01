#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module project_manager"""

# Imports - standard library
from argparse import Namespace
from typing import Tuple, Optional, NamedTuple, Any, Callable, List
from enum import Enum
from dataclasses import dataclass
import os, sys
from pathlib import Path
from datetime import datetime
import shutil

# Imports - 3rd party packages
import yamale
from yamale.schema.schema import Schema

# Imports - local source
from .logger import Logger, LogLevel, LoggerParams
from .path_helper import PathHelper

# TODO Use make_dataclass after reading all keys to dynamically create inputs database
# TODO There will be a separate outputs database that is generated and merged with inputs
# and spit out at the end of the job
# TODO Get resolution function working for reading in configs


@dataclass(frozen=True)
class ToolBoxParams:
    """All command line args to create ToolBox"""
    tools_file: str
    build_dir: str
    symlink: Optional[str]
    config: List[str]
    interactive: bool
    log_params: LoggerParams
    job: str


class ToolBox:
    """Coordinates the running of tools and jobs"""
    def __init__(self, args: ToolBoxParams) -> None:
        """Inializes project manager with global namespace from args list"""
        self._args = args
        # Make build directory and initialize logger
        self._build_dir = self.make_build_dir()
        self._logger = Logger(args.log_params)
        self.log = self._logger.log
        # Ensure that home directory is set
        self._home_dir = PathHelper.check_dir(os.getenv('TOOLBOX_HOME'))
        if self._home_dir is None:
            self.exit('TOOLBOX_HOME variable not set or incorrectly set.')
        # Populate Database
        self._db = self.generate_global_database()

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

    def validate_yaml(self, yaml_fname: str, schema_fname: str):
        """Checks to see if ooutput is an error message and exits if it is"""
        config = PathHelper.yamale_validate(yaml_fname, schema_fname)
        if isinstance(config, str):
            self.exit(config)
        return config

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

    def make_build_dir(self):
        """Make build directory and symlink"""
        date_str = datetime.now().strftime("%m-%d-%Y-%H:%M:%S")
        build_dir = Path(self._args.build_dir) / self._args.job / date_str
        build_dir = build_dir.resolve()
        build_dir.mkdir(parents=True, exist_ok=True)
        PathHelper.unlink_missing_ok(build_dir.parent / 'current')
        (build_dir.parent / 'current').symlink_to(build_dir,
                                                  target_is_directory=True)
        if self._args.symlink:
            PathHelper.unlink_missing_ok(Path(self._args.symlink))
            Path(self._args.symlink).symlink_to(build_dir.parents[1],
                                                target_is_directory=True)
        return build_dir

    def generate_global_database(self) -> dict:
        """Generates global database from config files and args"""
        tool_paths = self.validate_tools_file(self._args.tools_file)
        tool_configs = self.validate_tools(tool_paths)
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

    def validate_tools_file(self, fname: str) -> List[Path]:
        """Validates the tools file
        :param fname Filename of the tools file
        :return List of Paths to tools
        """
        # Load tools file (may include globals)
        tool_file = self.check_file(fname)
        if tool_file is None:
            self.exit(f'Cannot find tool file "{fname}"')
        schema_file = self.check_file(
            str(self._home_dir / "toolbox/schemas/tools.yml"))
        # Validate tool config
        tool_config = self.validate_yaml(str(tool_file), str(schema_file))
        # Exit if no valid tools found
        tool_paths = self.check_dirs(tool_config['tools'])
        if tool_paths == []:
            self.exit(f'No valid tools found in "{tool_file}"')
        return tool_paths

    def validate_tools(self, tool_paths: List[Path]) -> dict:
        """Iterateively builds tool config.
        All tools must validate before proceeding
        """
        tool_config = [
            self.validate_tool(tool_path) for tool_path in tool_paths
        ]
        return tool_config

    def validate_tool(self, tool_path: Path) -> Tuple[dict, dict]:
        """Individually validates a tool"""
        # Check and validate tool.yml
        tool_yml = self.check_file(tool_path / 'tool.yml')
        if tool_yml is None:
            self.exit(
                f'Tool at path "{tool_path}" does not contain required tool.yml file.'
            )
        yml = self.validate_yaml(
            str(tool_yml), str(self._home_dir / 'toolbox/schemas/tool.yml'))
        # Exit if tool cannot validate
        return yml

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
        shutil.copy(self._args.log_params.out_fname,
                    str(self._build_dir / self._args.log_params.out_fname))
