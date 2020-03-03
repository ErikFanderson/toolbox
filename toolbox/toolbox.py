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
import re
import copy

# Imports - 3rd party packages
import yaml
import yamale
from yamale.schema.schema import Schema

# Imports - local source
from .logger import Logger, LogLevel, LoggerParams
from .path_helper import PathHelper
from .dot_dict import DotDict
from .database import Database

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


class ToolBox(Database):
    """Coordinates the running of tools and jobs"""
    def __init__(self, args: ToolBoxParams) -> None:
        """Inializes project manager with global namespace from args list"""
        super().__init__()
        # Create logger and log function
        self._logger = Logger(args.log_params)
        self.log = self._logger.log
        # Ensure that home directory is set
        self._home_dir = PathHelper.check_dir(os.getenv('TOOLBOX_HOME'))
        if self._home_dir is None:
            self.exit('TOOLBOX_HOME variable not set or incorrectly set.')
        # Load args and make build directory
        self.load_dict({"args": args.__dict__})
        self._job_dir = self.make_build_dir()
        # Populate Database
        self.populate_database()

    def populate_database(self) -> dict:
        """Generates global database from config files and args"""
        self.load_tools()
        self.load_configs()
        self.check_db()
        ## combine_schemas
        ## check_configs
        ## return make_dataclass
        ##configs = args['config']
        ##self.combine_configs()

    def load_tools(self):
        """Loads tools and schemas into database"""
        # Check and add tools to database
        tool_paths = self.validate_tools_file(self.get_db("args.tools_file"))
        tool_config = self.validate_tools(tool_paths)
        self.load_dict(tool_config)

    def load_configs(self):
        """Loads all config files into database"""
        configs = self.check_files(self.get_db('args.config'))
        for config in configs:
            with open(config, 'r') as fp:
                self.load_dict(yaml.load(fp, Loader=yaml.SafeLoader))

    def check_db(self):
        """Checks database against default and provided schemas
        To be run after loading tools, configs, and performing resolution
        # TODO ultimately this should be rewritten to not perform validation
        serially... Construct large schema and run on entire database
        """
        schema = {}
        for tool_name, tool in self.get_db("tools").items():
            for prop_name, prop in tool['properties'].items():
                dot_str = f"tools.{tool_name}.{prop_name}"
                data = {f"{prop_name}": self.get_db(dot_str)}
                schema = {f"{prop_name}": prop["schema"]}
                err_msg = PathHelper.yamale_validate_dicts(data, schema)
                if isinstance(err_msg, str):
                    descr = prop["description"]
                    self.exit(
                        f'Invalid value for property "{dot_str}".\nDescription: {descr}{err_msg}'
                    )

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
        """Checks to see if output is an error message and exits if it is"""
        config = PathHelper.yamale_validate_files(yaml_fname, schema_fname)
        if isinstance(config, str):
            self.exit(config)
        return config

    def exit(self, msg: str) -> None:
        """Method for nicely erroring and exiting"""
        self.log(msg, LogLevel.ERROR)
        sys.exit(-1)

    def get_db(self, field: str) -> Any:
        """Attempts to get value from database"""
        success, value = super().get_db(field)
        if success:
            return value
        else:
            self.exit(f'Field "{field}" not found in internal database.')

    def make_build_dir(self):
        """Make build directory and symlink"""
        date_str = datetime.now().strftime("%m-%d-%Y-%H:%M:%S")
        build_dir = Path(
            self.get_db("args.build_dir")) / self.get_db("args.job") / date_str
        build_dir = build_dir.resolve()
        build_dir.mkdir(parents=True, exist_ok=True)
        PathHelper.unlink_missing_ok(build_dir.parent / 'current')
        (build_dir.parent / 'current').symlink_to(build_dir,
                                                  target_is_directory=True)
        if self.get_db("args.symlink"):
            PathHelper.unlink_missing_ok(Path(self.get_db("args.symlink")))
            Path(self.get_db("args.symlink")).symlink_to(
                build_dir.parents[1], target_is_directory=True)
        return build_dir

    #def resolve(self, configs: List[str]) -> dict:
    #    """Checks configs are valid files and resolves any ${}"""
    #    config_dict = DotDict()
    #    checked_configs = self.check_files(configs)
    #    for config in checked_configs:
    #        with open(config, 'r') as fp:
    #            data = yaml.load(fp, Loader=yaml.SafeLoader)
    #            config_dict.update(data)
    #    # Flatten and resolve
    #    config_dict.flatten()
    #    # Resolve steps
    #    # 1. Traverse entire namespace
    #    # 2. When hit string run recursive func to get value
    #    #   (beware circular AND do not allow replacement for list or dict)
    #    for config, value in config_dict.items():
    #        config_dict[config] = self.resolve_key(config, config, config_dict)
    #    # Expand
    #    config_dict.dot_expand()
    #    return config_dict

    #def resolve_key(self, key: str, og_key: str, config_dict: dict) -> Any:
    #    """Issues first resolve key recursive. Need separate for
    #    circular reference issue
    #    """
    #    key_ref = re.compile('\${(.*)}')
    #    config = config_dict[key]
    #    if isinstance(config_dict[key], str):
    #        for ref in key_ref.findall(config_dict[key]):
    #            new_ref = config_dict[ref]
    #    # TODO implement me
    #    elif isinstance(config_dict[key], list):
    #        pass
    #    # TODO implement me
    #    elif isinstance(config_dict[key], dict):
    #        pass
    #    return config

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
        # Validate each tool path and turn into dictionary
        tool_configs = [
            self.validate_tool(tool_path) for tool_path in tool_paths
        ]
        # Combine into single dictionary using names as keys
        tool_config = {"tools": {}}
        for tool in tool_configs:
            tool_name = list(tool.keys())[0]
            if tool_name in list(tool_config['tools'].keys()):
                self.exit(
                    f'Tool w/ name "{tool_name}" defined multiple times.')
            tool_config['tools'].update(tool)
        return tool_config

    def validate_tool(self, tool_path: Path) -> dict:
        """Individually validates a tool"""
        # Check and validate tool.yml
        tool_yml = self.check_file(tool_path / 'tool.yml')
        if tool_yml is None:
            self.exit(
                f'Tool at path "{tool_path}" does not contain required tool.yml file.'
            )
        yml = self.validate_yaml(
            str(tool_yml), str(self._home_dir / 'toolbox/schemas/tool.yml'))
        # Change dictionary before merging with other tools
        tool_name = yml["name"]
        del yml["name"]
        tool_config = {tool_name: yml}
        for prop_name, prop in yml["properties"].items():
            tool_config[tool_name][prop_name] = prop['default']
        return tool_config

    def execute(self):
        """Runs the job!"""
        # Copy log file to build directory
        shutil.copy(
            self.get_db("args.log_params").out_fname, str(self._job_dir))
