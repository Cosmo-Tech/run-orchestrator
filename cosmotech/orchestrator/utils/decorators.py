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
