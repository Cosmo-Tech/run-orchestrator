# Copyright (C) - 2023 - 2023 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import os
from functools import wraps


def require_env(envvar, envvar_desc):
    def wrap_function(func):
        @wraps(func)
        def f(*args, **kwargs):
            if envvar not in os.environ:
                raise EnvironmentError(f"Missing the following environment variable: {envvar}")
            return func(*args, **kwargs)

        f.__doc__ = "\n".join(
            [f.__doc__ or "", f"Requires env var `{envvar:<15}` *{envvar_desc}*  "])
        return f

    return wrap_function
