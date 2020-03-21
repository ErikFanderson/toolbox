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
        Tool.__init__(self, db, log)
        fsl = FileSystemLoader([
            os.path.join(self.get_db("internal.tools.JinjaTool.path"),
                         "templates")
        ] + self.get_db(f'jinja.template_directories'))
        self.env = Environment(loader=fsl,
                               undefined=StrictUndefined,
                               trim_blocks=True,
                               lstrip_blocks=True)
        # Add some filters (names are same as ansible filters...)
        self.env.filters["realpath"] = realpath_filter
        self.env.filters["realpathjoin"] = realpath_join_filter

    @staticmethod
    def add_template_dirs(db: Database, dirs: List[str]):
        """Adds directories to jinja directories portion of database"""
        # Check to make sure they are actually directories
        for d in dirs:
            d = Path(d).resolve()
            if not d.is_dir():
                raise ToolError(f'Jinja tool cannot find directory "{d}"')
        # Update database
        templates = dirs + db.get_db("jinja.template_directories")
        db.load_dict({"jinja.template_directories": templates})

    def render_to_file(self, template: str, outfile: str, **kwargs: Any):
        """Gets template from environment and renders
        :param template template to be used
        :param outfile Name/path of output file
        :param kwargs Key word arguments to be passed to jinja2 template
        """
        with open(outfile, 'w') as fp:
            fp.write(self.render(template, **kwargs))
        self.log(
            f'Successfully rendered file "{Path(outfile).relative_to(self.get_db("internal.work_dir"))}"'
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
        template = self.env.get_template(template)
        return template.render(**kwargs, _uname=uname, _date=date)
