
''' A module for decorators. '''

import inspect
from decorator import decorator

@decorator
def memoize(function, *args, **kwargs):
    ''' A decorator that memoizes a function. '''
    
    inputs = inspect.getcallargs(function, *args, **kwargs)  # pylint: disable=deprecated-method
    self = inputs.pop('self', function)  # We test whether function is a method by looking for a `self` argument. If not we store the cache in the function itself.
    
    if not hasattr(self, '_cache'):
        self._cache = dict()
    key = (function.__name__, frozenset(inputs.items()))
    if key not in self._cache:
        try:
            self._cache[key] = function(*args, **kwargs)
        except Exception as error:  # pylint: disable=broad-except
            if isinstance(error, KeyboardInterrupt):
                raise
            self._cache[key] = error
    
    result = self._cache[key]
    if isinstance(result, Exception):
        raise result
    else:
        return result

