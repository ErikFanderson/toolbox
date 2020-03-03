#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Erik Anderson
# Email: erik.francis.anderson@gmail.com
# Date: 02/29/2020
"""Docstring for module logger"""

# Imports - standard library
from dataclasses import dataclass
from enum import Enum
import logging
from logging import Formatter
from typing import Optional

# Imports - 3rd party packages

# Imports - local source


class LogLevel(Enum):
    """Same logging levels used by python logging module (PRINT disables logging)"""
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass(frozen=True)
class LoggerParams:
    """All necessary database parameters for creating a logger
    All parameters specified through global database (db should have defaults for some)
    """
    level: LogLevel
    out_fname: Optional[str] = None
    name: str = "default"
    formatter: str = "[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s"


class Logger:
    """Configurable logger for ToolBox"""
    def __init__(self, p: LoggerParams) -> None:
        """Initializes a logger using db values from project manager"""
        self.p = p
        self._logger = logging.getLogger(p.name)
        self._logger.setLevel(p.level.value)
        formatter = Formatter(p.formatter)
        # Output file setup
        if p.out_fname:
            self.file_handler = logging.FileHandler(p.out_fname, mode='w')
            self.file_handler.setFormatter(formatter)
            self._logger.addHandler(self.file_handler)
        # Stream Handler setup
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(formatter)
        self._logger.addHandler(self.stream_handler)

    def log(self,
            msg: str,
            level: LogLevel = LogLevel.INFO,
            prefix: Optional[str] = None) -> None:
        """Basic log function for logger class
        :param msg Message to be logged
        :param level LogLevel to use when logging msg
        :param prefix Will add prefix to the logger formatter
        """
        # Update formatter
        if prefix:
            if self.p.out_fname:
                self.file_handler.setFormatter(
                    Formatter(f"{prefix} %(message)s"))
            self.stream_handler.setFormatter(
                Formatter(f"{prefix} %(message)s"))
        else:
            if self.p.out_fname:
                self.file_handler.setFormatter(Formatter(self.p.formatter))
            self.stream_handler.setFormatter(Formatter(self.p.formatter))
        # Log information
        if self._logger.level == LogLevel.NOTSET.value:
            print(msg)
        else:
            self._logger.log(level.value, msg)
