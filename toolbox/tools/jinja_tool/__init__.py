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
from toolbox.utils import Validator


class JinjaTool(Tool):
    """Base jinja Tool w/ render function. Still Abstract"""
    def __init__(self,
                 db: Database,
                 log: Callable[[str, LogLevel], None],
                 extra_template_dirs: List[str] = []):
        """Creates a jinja2 environment for this module
        :param package The package that this module resides in
        :param templates The path to the templates dir relative to the package
        """
        Tool.__init__(self, db, log)
        dirs = self.check_dirs(
            self.get_db('tools.JinjaTool.template_directories'))
        dirs += extra_template_dirs
        fsl = FileSystemLoader(dirs)
        self.env = Environment(loader=fsl, undefined=StrictUndefined)

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
