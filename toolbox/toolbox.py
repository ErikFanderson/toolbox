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


class ToolBoxError(Exception):
    """KeyError for internal database"""
    pass


@dataclass(frozen=True)
class ToolSchema:
    """simple dataclass for tool_schema"""
    tool: str
    namespace: str
    properties: dict
    path: str
    schema_includes: Optional[List[str]] = None


@dataclass(frozen=True)
class Task:
    """simple dataclass for Task (substep of job)"""
    tool: str
    additional_configs: Optional[List[str]] = None


@dataclass(frozen=True)
class ToolBoxParams:
    """All command line args to create ToolBox"""
    build_dir: str
    symlink: Optional[str]
    config: List[str]
    log_params: LoggerParams
    out_fname: str
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
        self._load_dict({"internal.env": os.environ})
        self._load_dict({"internal.tools": {}})
        self.restricted_ns = ["jobs", "user", "tools", "toolbox"]
        # Populate Database
        self.populate_database()
        atexit.register(self.exit)

    def populate_database(self) -> dict:
        """Generates global database from config files and args"""
        # Load empty restricted namespaces (just so that they exist)
        for ns in self.restricted_ns:
            self.load_dict({f"{ns}": {}})
        # Run initial load to allow for resolving of tool paths
        self.load_configs(False, False)
        # Load all default property values for tools
        self.load_tools()
        # Load configs again to overwrite default values
        self.load_configs()
        # Check jobs - Validate jobs yaml
        self.validate_db(
            os.path.join(self.get_db('internal.home_dir'),
                         'toolbox/schemas/toolbox.yml'))

    def log(self,
            msg: str,
            level: LogLevel = LogLevel.INFO,
            prefix: Optional[str] = None) -> None:
        """Function for logging information"""
        self._log(msg, level)

    def load_configs(self,
                     error_on_unresolved: bool = True,
                     print_info: bool = True):
        """Loads all config files into database"""
        # Load user specified config files
        configs = self.check_files(self.get_db('internal.args.config'))
        autoload_file = self.check_file(
            os.path.join(self.get_db('internal.work_dir'), "toolbox.yml"))
        configs = configs + [autoload_file] if autoload_file else configs
        for config in configs:
            self.load_config(config)
            if print_info:
                self.log(f'Loaded configuration file "{config}"',
                         LogLevel.INFO)
        self._db.resolve(error_on_unresolved)

    def load_config(self, config: Union[str, Path]):
        """Method for loading config to db. Exists in case this
        behavior needs to change in the future.
        """
        with open(config, 'r') as fp:
            self.load_dict(yaml.load(fp, Loader=yaml.SafeLoader))

    def load_tools(self):
        """Loads tools and schemas into database as well as default properties for tools"""
        # Check that tools are valid
        tool_paths = self.check_dirs(self.get_db("tools"))
        # Verify that tools have proper tool.yml
        tool_schemas = {}
        namespaces = []
        for tp in tool_paths:
            cfg = self.validate_yaml(
                os.path.join(tp, "tool.yml"),
                os.path.join(self.get_db('internal.home_dir'),
                             'toolbox/schemas/tool.yml'))
            if "schema_includes" not in cfg:
                cfg["schema_includes"] = None
            ts = ToolSchema(**cfg, path=str(tp))
            # Upload TS to internal
            self._load_dict({f"internal.tools.{cfg['tool']}": ts.__dict__})
            # Verify namespace
            ns = cfg['namespace']
            ns_dict = {}
            if ns in namespaces:
                raise ToolBoxError(f'Namespace "{ns}" defined multiple times')
            elif ns in self.restricted_ns:
                raise ToolBoxError(
                    f'Namespace "{ns}" is used by toolbox and cannot be used as a tool namespace'
                )
            # upload namespace
            namespaces.append(ns)
            for prop_name, prop in cfg["properties"].items():
                ns_dict[prop_name] = prop["default"]
            self.load_dict({f"{ns}": ns_dict})

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
            tool_path = Path(self.get_db(f"internal.tools.{tool}.path"))
            sys.path.insert(1, str(tool_path.parent))
        # Export environment variables
        if "export" in self.get_db("toolbox"):
            for k, v in self.get_db("toolbox.export").items():
                os.environ[k] = v
                self.log(f"Exported: {k} = {v}")
        # Run all tasks in job
        job = self.get_db(f'jobs.{self.get_db("internal.args.job")}')
        for task in job["tasks"]:
            self.run_task(Task(**task))
        self.cleanup()
