#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module cli_driver"""

# Imports - standard library
import argparse

# Imports - 3rd party packages

# Imports - local source
from project_manager import ProjectManager

#import os,sys
#import argparse
#from pathlib import Path
#from sympy.parsing.sympy_parser import parse_expr
#import copy
#from pysilicon.file_gen import *
#import math
#import re
#import yaml


class PyProjectCLIDriver:
    """Command line driver for pyproject invocation"""
    def parse_args(self) -> argparse.Namespace:
        ''' Parse arguments for PyProjectCLIDriver CLI Driver'''
        parser = argparse.ArgumentParser(
            description=
            "Completes yaml decribed jobs using python described tools")
        parser.add_argument('job',
                            help='Specifies the job (*.yml) to be executed.')
        parser.add_argument(
            '-b',
            '--build-dir',
            default='build',
            help=
            'Specifies the build/outputs directory for all jobs. Default: build/'
        )
        parser.add_argument(
            '-ln',
            '--symlink',
            required=False,
            help='Optionally define a symlink build directory location.')
        parser.add_argument(
            '-c',
            '--config',
            help=
            'Pass a configuration file (*.yml) to be included in global namespace.'
        )
        return parser.parse_args()

    def main(self) -> None:
        """Creates project manager and launches job"""
        args = self.parse_args()
        pm = ProjectManager(vars(args))


if __name__ == '__main__':
    PyProjectCLIDriver().main()
