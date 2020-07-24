"""
Exceptions for bonsai3py
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict


class RetryTimeoutError(Exception):
    pass


class ServiceError(Exception):
    pass
