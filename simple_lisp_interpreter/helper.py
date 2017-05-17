# -*- coding: utf-8 -*-

from .const import Symbol


def require(x, predicate, msg='Incorrect length'):
    """
    Helper function to check where predicate of x is satified,
    with error message output.
    """
    if not predicate:
        raise SyntaxError('{}: {}'.format(to_lisp_string(x), msg))


def to_lisp_string(obj):
    if obj is True:
        return '#t'
    elif obj is False:
        return '#f'
    elif isinstance(obj, Symbol):
        return obj
    elif isinstance(obj, str):
        return obj.replace('"', '\"')
    elif isinstance(obj, (list, tuple)):
        return '(' + ' '.join(map(to_lisp_string, obj)) + ')'
    elif isinstance(obj, complex):
        return str(obj).replace('j', 'i')
    else:
        return str(obj)
