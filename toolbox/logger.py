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
    name: str = "default_logger_name"
    formatter: str = "[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s"


class Logger:
    """Configurable logger for ToolBox"""
    def __init__(self, p: LoggerParams) -> None:
        """Initializes a logger using db values from project manager"""
        self._logger = logging.getLogger(p.name)
        self._logger.setLevel(p.level.value)
        formatter = logging.Formatter(p.formatter)
        # Output file setup
        if p.out_fname:
            file_handler = logging.FileHandler(p.out_fname, mode='w')
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        # Stream Handler setup
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self._logger.addHandler(stream_handler)

    def log(self, msg: str, level: LogLevel = LogLevel.INFO) -> None:
        """Basic log function for logger class
        :param msg Message to be logged
        :param level LogLevel to use when logging msg
        """
        if self._logger.level == LogLevel.NOTSET.value:
            print(msg)
        else:
            self._logger.log(level.value, msg)
