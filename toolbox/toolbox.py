#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module project_manager"""

# Imports - standard library
from argparse import Namespace
from typing import Union, Tuple, Optional, NamedTuple, Any, Callable, List
from enum import Enum
from dataclasses import dataclass
import os, sys
from pathlib import Path
from datetime import datetime
import shutil
import re
import copy
import importlib
import atexit

# Imports - 3rd party packages
import yaml
import yamale
from yamale.schema.schema import Schema

# Imports - local source
from .logger import Logger, HasLogFunction, LogLevel, LoggerParams
from .utils import *
from .dot_dict import DotDict
from .database import Database
from .tool import Tool

# TODO Get resolution function working for reading in configs


class ToolBoxError(Exception):
    """KeyError for internal database"""
    pass


@dataclass(frozen=True)
class ToolSchema:
    """simple dataclass for tool_schema"""
    name: str
    schema_path: str  # Path to tool schema file
    properties: dict
    is_tool: bool
    path: Optional[str] = None  # Path to tool module directory
    schema_includes: Optional[List[str]] = None
    additional_schemas: Optional[List[str]] = None


@dataclass(frozen=True)
class Task:
    """simple dataclass for Task (substep of job)"""
    tool: str
    additional_configs: Optional[List[str]] = None


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


class ToolBox(Database, HasLogFunction):
    """Coordinates the running of tools and jobs"""
    def __init__(self, args: ToolBoxParams) -> None:
        """Inializes project manager with global namespace from args list"""
        super().__init__("internal")
        # Create logger and log function
        self._logger = Logger(args.log_params)
        self._log = self._logger.log
        # Ensure that home directory is set
        home_dir = check_dir(os.getenv('TOOLBOX_HOME'))
        if home_dir is None:
            raise ToolBoxError(
                'TOOLBOX_HOME variable not set or incorrectly set.')
        # Load internal.args and make build directory
        self._load_dict({"internal.command": ' '.join(sys.argv[1:])})
        self._load_dict({"internal.args": args.__dict__})
        self._load_dict({"internal.home_dir": str(home_dir)})
        self._load_dict({"internal.work_dir": str(Path('.').resolve())})
        self._load_dict({"internal.job_dir": self.make_build_dir()})
        self._load_dict({"internal.tools": {}})
        self.load_dict({"tools": {}})
        # Populate Database
        self.populate_database()
        atexit.register(self.exit)

    def populate_database(self) -> dict:
        """Generates global database from config files and args"""
        self.load_tools()
        self.load_configs()
        # Check jobs - Validate yaml and check that each tool is found in tools file
        self.validate_db(
            os.path.join(self.get_db('internal.home_dir'),
                         'toolbox/schemas/jobs.yml'))

    def log(self,
            msg: str,
            level: LogLevel = LogLevel.INFO,
            prefix: Optional[str] = None) -> None:
        """Function for logging information"""
        self._log(msg, level)

    def load_tools(self):
        """Loads tools and schemas into database"""
        # Check and add tools to database
        tool_paths = self.validate_tools_file(
            self.get_db("internal.args.tools_file"))
        # Get unique schemas
        unique_tool_schemas = self.get_unique_tool_schemas(tool_paths)
        for ts in unique_tool_schemas:
            self.add_tool_schema(ts)

    def get_unique_tool_schemas(self,
                                tool_paths: List[Path]) -> List[ToolSchema]:
        """Returns a list of unique_tools from given tool set"""
        # Return full paths to all schemas (recursively)
        tool_schemas_by_path = []
        for tool_path in tool_paths:
            tool_schemas_by_path.append(
                self.get_tool_schemas(str(tool_path / 'tool.yml'),
                                      self.get_db('internal.work_dir'), {},
                                      is_tool=True))
        # Uniquify across all the tools
        unique_tool_schemas = {}
        for tool_schema_dict in tool_schemas_by_path:
            for path, ts in tool_schema_dict.items():
                unique_tool_schemas.update({path: ts})
        return [v for k, v in unique_tool_schemas.items()]

    def get_tool_schemas(self,
                         tool_schema: str,
                         current_dir: str,
                         current_dict: dict,
                         is_tool: bool = False):
        """recursively gets all referenced tool schema_includes
        :param tool_schema path to the tool_schema
        :param current_dir current directory that the tool schema path is relative to
        :param current_list list of tools that the function appends to
        """
        # Check to make sure valid path and yaml is valid
        tool_schema_path = self.check_file(str(
            Path(current_dir) / tool_schema))
        if tool_schema_path is None:
            raise ToolBoxError(
                f'Tool Schema at path "{tool_schema_path}" is not a valid file.'
            )
        yml = self.validate_yaml(
            str(tool_schema_path),
            os.path.join(self.get_db('internal.home_dir'),
                         'toolbox/schemas/tool.yml'))
        # If has additional schemas then recurse
        if "additional_schemas" in yml:
            for add_schema in yml["additional_schemas"]:
                current_dict = self.get_tool_schemas(
                    add_schema, str(tool_schema_path.parent), current_dict)
        # Populate yml for ToolSchema creating
        yml["schema_path"] = str(tool_schema_path)
        yml["is_tool"] = is_tool
        if is_tool:
            yml["path"] = str(tool_schema_path.parent)
            yml["additional_schemas"] = []
            for k, v in current_dict.items():
                yml["additional_schemas"].append(v.name)
        tool_schema = ToolSchema(**yml)
        # Uniquify by schema path
        current_dict.update({yml["schema_path"]: tool_schema})
        return current_dict

    def add_tool_schema(self, tool_schema: ToolSchema):
        """Adds schema to internal Database
        Basically adds a new namespace to database w/ default values
        and schemas.
        :param path_to_schema This is the path to the schema file to add
        :param add_to_internal Optionally adds this to internal.
        Should only add to internal if this is also in tools file
        """
        # Check to make sure that schema tool name does not already exist
        if tool_schema.name in self.get_db("tools"):
            raise ToolBoxError(
                f'Tool schema w/ name "{tool_schema.name}" defined multiple times.'
            )

        # Update internal database with original tool_schema dict
        self._load_dict(
            {f"internal.tools.{tool_schema.name}": tool_schema.__dict__})

        # Update external tool database (schema or tool)
        tool_config = {}
        for prop_name, prop in tool_schema.properties.items():
            tool_config[prop_name] = prop['default']
        self.load_dict({f"tools.{tool_schema.name}": tool_config})

    def load_configs(self):
        """Loads all config files into database"""
        configs = self.check_files(self.get_db('internal.args.config'))
        for config in configs:
            self.load_config(config)
        self._db.resolve()

    def load_config(self, config: Union[str, Path]):
        """Method for loading config to db. Exists in case this
        behavior needs to change in the future.
        """
        with open(config, 'r') as fp:
            self.load_dict(yaml.load(fp, Loader=yaml.SafeLoader))

    def validate_db(self, fname):
        """Runs database against schema in file fname"""
        err_msg = YamaleValidator.validate_dict_with_file(self._db, fname)
        if isinstance(err_msg, str):
            raise ToolBoxError(f"Error validating internal database.{err_msg}")

    def validate_yaml(self, yaml_fname: str, schema_fname: str):
        """Checks to see if output is an error message and exits if it is"""
        config = YamaleValidator.validate_files(yaml_fname, schema_fname)
        if isinstance(config, str):
            raise ToolBoxError(config)
        return config

    def exit(self) -> None:
        """Method for nicely erroring and exiting"""
        self.cleanup()

    def get_db(self, field: str) -> Any:
        """Attempts to get value from database"""
        success, value = super().get_db(field)
        if success:
            return value
        else:
            raise ToolBoxError(
                f'Field "{field}" not found in internal database.')

    def make_build_dir(self):
        """Make build directory and symlink"""
        date_str = datetime.now().strftime("%m-%d-%Y-%H:%M:%S")
        build_dir = Path(self.get_db("internal.args.build_dir")) / self.get_db(
            "internal.args.job") / date_str
        build_dir = build_dir.resolve()
        build_dir.mkdir(parents=True, exist_ok=True)
        unlink_missing_ok(build_dir.parent / 'current')
        (build_dir.parent / 'current').symlink_to(build_dir,
                                                  target_is_directory=True)
        if self.get_db("internal.args.symlink"):
            unlink_missing_ok(Path(self.get_db("internal.args.symlink")))
            Path(self.get_db("internal.args.symlink")).symlink_to(
                build_dir.parents[1], target_is_directory=True)
        return str(build_dir)

    def validate_tools_file(self, fname: str) -> List[Path]:
        """Validates the tools file
        :param fname Filename of the tools file
        :return List of Paths to tools
        """
        # Load tools file (may include globals)
        tool_file = self.check_file(fname)
        if tool_file is None:
            raise ToolBoxError(f'Cannot find tool file "{fname}"')
        schema_file = self.check_file(
            os.path.join(self.get_db('internal.home_dir'),
                         "toolbox/schemas/tools.yml"))
        # Validate tool config
        tool_config = self.validate_yaml(str(tool_file), str(schema_file))
        tool_paths = self.check_dirs(tool_config['tools'])
        return tool_paths

    def cleanup(self):
        """Performs any actions required before exiting program"""
        # Copy log file to build directory
        if self.get_db("internal.args.log_params").out_fname:
            shutil.copy(
                self.get_db("internal.args.log_params").out_fname,
                str(self.get_db('internal.job_dir')))

    def run_task(self, task: Task) -> None:
        """Runs the task (i.e. subcomponent of a job)"""
        # Check to make sure that tool actually exists
        if task.tool not in list(self.get_db('internal.tools').keys()):
            raise ToolBoxError(
                f'Job "{self.get_db("internal.args.job")}" cannot find Tool "{task.tool}"'
            )
        # Issue starting log message
        self.log(
            f'Starting task "{task.tool}" of job "{self.get_db("internal.args.job")}".'
        )
        # Save current state of database
        original_db = copy.deepcopy(self._db)
        # Load in additional configs and rerun db validation
        if task.additional_configs:
            for config in task.additional_configs:
                self.load_config(config)
                self.log(
                    f'Additional configuration file "{config}" successfully loaded.'
                )
        self._db.resolve()
        # Instantiate tool class
        tool_path = Path(self.get_db(f"internal.tools.{task.tool}.path"))
        tool_module = importlib.import_module(tool_path.stem)
        ToolClass = getattr(tool_module, task.tool)
        tool = ToolClass(self, self.log)
        if not isinstance(tool, Tool):
            raise ToolBoxError(
                f'Tool "{task.tool}" is not a sub-class of Tool.')
        # Log step function for steps
        def log_step(msg: str, step: str, level: LogLevel) -> None:
            prefix = f"[{self.get_db('internal.args.job')}] [{task.tool}] [{step}] [%(levelname)s]"
            self.log(msg, level, prefix)

        # Run steps within task [job] [tool] [step]
        for step in tool.steps():
            log_fn = lambda msg, level: log_step(
                msg=msg, step=step.__name__, level=level)
            tool.set_log_fn(log_fn)
            self.log(f'Running step "{step.__name__}"')
            step()
        # Reload original contents of database
        self._db = original_db

    def execute(self):
        """Runs the job!"""
        # Load tools into python path
        for tool in list(self.get_db("internal.tools").keys()):
            if self.get_db(f"internal.tools.{tool}.is_tool"):
                tool_path = Path(self.get_db(f"internal.tools.{tool}.path"))
                sys.path.insert(1, str(tool_path.parent))
        # Run all tasks in job
        tasks = self.get_db(f'jobs.{self.get_db("internal.args.job")}')
        for task in tasks:
            self.run_task(Task(**task))
        self.cleanup()
