__version__ = "0.3.0"

# Everything is aliases with a leading underscore so as to not pollute the akashic_records namespace
from functools import wraps as _wraps
import inspect as _inspect
from typing import Optional as _Optional
from akashic_records._meta import injector as _injector
from akashic_records._meta import dynamic_function as _dynamic_function
import sys as _sys

from akashic_records._meta.errors import ExhaustedAttemtpsError as _ExhaustedAttemtpsError
from akashic_records._meta.errors import MultiError as _MultiError

config = _injector.Loader()
_finder = _injector.Finder(config)
_sys.meta_path.append(_finder)

def generate(n: _Optional[int] = None, temperature: _Optional[float] = None, max_tokens: _Optional[int] = None):
    '''
    Decorator for dynamic function generation

    Parameters:
    -----------
    n : int, optional
        The number of completions to generate at once
    temperature : float, optional
        The temperature of the completion generation 
    max_tokens : int, optional
        The maximum tokens that a completion can have

    Returns:
    --------
    Callable
        A configured decorator to dynamically generate functions
    '''
    def outer(f):
        '''
        Decorator for dynamic function generation

        Parameters:
        -----------
        f : Callable
            Function with the following structure
            @generate
            def quick_sort(arr: list) -> list:
                """
                Sorts the input list using the quicksort algorithm.

                Parameters:
                -----------
                arr : list
                    The input list to be sorted.

                Returns:
                --------
                list
                    The sorted list.
                """
                ...
        Returns:
        --------
        Callable
            A generated function
        '''
        _n = n or config.n
        _temperature = temperature or config.temperature
        _max_tokens = max_tokens or config.max_tokens

        docstring = _inspect.cleandoc(f.__doc__)
        sig = _inspect.signature(f)
        builder = _dynamic_function.CodeBuilder(_n, _temperature, _max_tokens)
        dyn = None

        @_wraps(f)
        def inner(*args, **kwargs):
            nonlocal dyn
            if not dyn:
                attempt = config.attempts
                errors = _MultiError()
                # Intentionally brittle check to allow for unlimited attempts using any negative number
                while attempt != 0:
                    attempt -= 1
                    for func in builder.build_function(
                        f.__name__, sig, docstring
                    ):
                        try:
                            result = func(*args, **kwargs)
                            dyn = func
                            return result
                        except Exception as e:
                            errors.append(e)
                            # TODO: log
                            pass
                raise _ExhaustedAttemtpsError(
                    f"Was not able to generate valid {f.__name__} function after {config.attempts} attempts.\n"
                    "If implementations are cut off early consider increasing max_tokens"
                ) from errors
            else:
                return dyn(*args, **kwargs)
        return inner
    return outer
