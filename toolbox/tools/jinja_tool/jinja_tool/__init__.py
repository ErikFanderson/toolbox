#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 03/02/2020
"""Docstring for module jinja tool """

# Imports - standard library
import os
from abc import ABC, abstractmethod
from typing import List, Callable, Any, Optional
from pathlib import Path
import getpass
from datetime import datetime
import shutil

# Imports - 3rd party packages
from jinja2 import StrictUndefined, FileSystemLoader, Environment

# Imports - local source
from toolbox.database import Database
from toolbox.logger import LogLevel, HasLogFunction
from toolbox.tool import Tool, ToolError
from toolbox.utils import Validator


def realpath_filter(text: str) -> str:
    """Realpath filter for jinja2
    Resolves path and returns the absolute path
    """
    return str(Path(text).resolve())


def realpath_join_filter(items: List[str], join_arg: str) -> str:
    """Realpath filter for jinja2
    Resolves path and returns the absolute path
    """
    return join_arg.join([str(Path(item).resolve()) for item in items])


class JinjaTool(Tool):
    """Base jinja Tool w/ render function. Still Abstract"""
    def __init__(self, db: Database, log: Callable[[str, LogLevel], None]):
        """Creates a jinja2 environment for this module
        :param package The package that this module resides in
        :param templates The path to the templates dir relative to the package
        """
        super(JinjaTool, self).__init__(db, log)
        # Create templates dir in job dir
        self.templates_dir = os.path.join(self.get_db("internal.job_dir"),
                                          "jinja_templates")
        Path(self.templates_dir).mkdir(parents=True, exist_ok=True)
        # Add all tool templates
        for t in self.tools:
            d = os.path.join(self.get_db(f'internal.tools.{t}.path'),
                             "templates")
            if os.path.isdir(d):
                self.add_jinja_templates([str(f) for f in Path(d).glob("*")])
        # Add additional templates
        self.add_jinja_templates(
            self.get_db(
                self.get_namespace("JinjaTool") + ".additional_templates"))
        # Create environment
        fsl = FileSystemLoader([self.templates_dir])
        self.env = Environment(loader=fsl,
                               undefined=StrictUndefined,
                               trim_blocks=True,
                               lstrip_blocks=True)
        # Add some filters (names are same as ansible filters...)
        self.env.filters["realpath"] = realpath_filter
        self.env.filters["realpathjoin"] = realpath_join_filter

    def add_jinja_templates(self, files: List[str]):
        """Adds templates to jinja directories portion of database"""
        # Check to make sure they are actually directories
        for f in files:
            f = Path(f).resolve()
            if not f.is_file():
                raise ToolError(f'Jinja tool cannot find file "{f}"')
            shutil.copy(str(f), os.path.join(self.templates_dir, f.name))

    def render_to_file(self, template: str, outfile: str, **kwargs: Any):
        """Gets template from environment and renders
        :param template template to be used
        :param outfile Name/path of output file
        :param kwargs Key word arguments to be passed to jinja2 template
        """
        with open(outfile, 'w') as fp:
            fp.write(self.render(template, **kwargs))
        rel_outfile = os.path.relpath(outfile, self.get_db("internal.work_dir"))
        self.log(
            f'Successfully rendered file "{rel_outfile}"'
        )

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
        template = self.env.get_template(Path(template).name)
        return template.render(**kwargs, _uname=uname, _date=date)
