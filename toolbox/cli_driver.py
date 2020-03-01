#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/27/2020
"""Docstring for module cli_driver"""

# Imports - standard library
import argparse
from dataclasses import dataclass

# Imports - 3rd party packages

# Imports - local source
from toolbox import ToolBox, ToolBoxParams
from logger import LogLevel

#import os,sys
#import argparse
#from pathlib import Path
#from sympy.parsing.sympy_parser import parse_expr
#import copy
#from pysilicon.file_gen import *
#import math
#import re
#import yaml


class ToolBoxCLIDriver:
    """Command line driver for pyproject invocation"""
    def parse_args(self) -> argparse.Namespace:
        ''' Parse arguments for PyProjectCLIDriver CLI Driver'''
        parser = argparse.ArgumentParser(description="Runs jobs using tools")
        parser.add_argument('job',
                            help='Specifies job (*.yml) to be executed.')
        parser.add_argument(
            '-t',
            '--tool-file',
            default='tools.yml',
            help='Specifies the tool file to be used. Default: tools.yml')
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
            help='Optionally define a symlink build directory location.')
        parser.add_argument(
            '-c',
            '--config',
            action='append',
            help=
            'Pass a configuration file (*.yml) to be included in global namespace.'
        )
        parser.add_argument(
            '-i',
            '--interactive',
            action='store_true',
            help=
            'Opens interactive session to query internal database before execution.'
        )
        parser.add_argument(
            '-l',
            '--log-level',
            default='info',
            choices=('notset', 'info', 'debug', 'warning', 'error',
                     'critical'),
            help='Specifies the global logging level. Default: info')
        return parser.parse_args()

    def main(self) -> None:
        """Creates project manager and launches job"""
        args = self.parse_args()
        tb_args = ToolBoxParams(args.tool_file, args.build_dir, args.symlink,
                                args.config, args.interactive,
                                LogLevel[(args.log_level).upper()])
        tb = ToolBox(tb_args)


if __name__ == '__main__':
    ToolBoxCLIDriver().main()
