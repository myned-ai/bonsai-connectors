"""
Logging for bonsai3py
Copyright 2020 Microsoft
"""

from datetime import datetime
import sys
from time import time
from typing import Any, Dict, Optional


class Logger:
    """
    Entry point for runtime logging to custom and predefined domains.

    Custom domains like the one defined in the following example can be
    enabled from the command line (see `ServiceConfig`) or by calling
    `Logger.set_enabled`.

    Example Usage:

    ```
    from bonsai3.logger import Logger

    log = Logger()

    def foo(*args, **kwargs):
        log.set_enabled("mydomain")

    def bar(*args, **kwargs):
        log.mydomain("Hello, World!")
    ```
    """

    _impl = None # type: Optional[Dict[str, Any]]

    def __init__(self):
        if self._impl is None:
            self._enabled_keys = {
                'error': True,
                'info':  True
            }
            self._enable_all = False
            self.__class__._impl = self.__dict__
        else:
            self.__dict__ = self._impl

    def __getattr__(self, attr: Any):
        if self._enable_all or self._enabled_keys.get(attr, False):
            ts = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")
            return lambda msg: \
                sys.stderr.write("[{0}][{1}] {2}\n".format(ts, attr, msg))
        else:
            return lambda msg: None

    def set_enabled(self, key, enable=True):
        """
        Enable or disable the given logging domain.

        Arguments:
            key: `string`
            enable: `bool`
        """
        self.__class__._impl['_enabled_keys'][key] = enable

    def set_enable_all(self, enable_all):
        """
        Enable or disable verbose logging.

        After passing `True` to this method, any invocation of the form
        `Logger().<domain>` will result in a printed log line, regardless of
        whether `Logger.set_enabled` was ever called for that particular
        domain.

        Arguments:
            enable_all: `bool`
        """
        self.__class__._impl['_enable_all'] = enable_all
