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
from .toolbox import ToolBox, ToolBoxParams
from .logger import LogLevel, LoggerParams


class ToolBoxCLIDriver:
    """Command line driver for pyproject invocation"""
    def parse_args(self) -> argparse.Namespace:
        ''' Parse arguments for PyProjectCLIDriver CLI Driver'''
        parser = argparse.ArgumentParser(description="Runs jobs using tools")
        parser.add_argument('job',
                            help='Specifies job (*.yml) to be executed.')
        parser.add_argument(
            '-t',
            '--tools-file',
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
        parser.add_argument(
            '-o',
            '--output',
            default='toolbox',
            help='Specifies the log filename. Default: toolbox.log')
        return parser.parse_args()

    def main(self) -> None:
        """Creates project manager and launches job"""
        args = self.parse_args()
        logger_params = LoggerParams(level=LogLevel[(args.log_level).upper()],
                                     out_fname=args.output + '.log')
        tb_args = ToolBoxParams(args.tools_file, args.build_dir, args.symlink,
                                args.config, args.interactive, logger_params,
                                args.job)
        tb = ToolBox(tb_args)
        tb.execute()


if __name__ == '__main__':
    ToolBoxCLIDriver().main()
