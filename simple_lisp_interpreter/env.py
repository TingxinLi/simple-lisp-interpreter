# -*- coding: utf-8 -*-

import math
import operator as op

from .const import Number, Symbol


class Env(dict):

    def __init__(self, params=(), args=(), outer=None):
        assert(len(params) == len(args))
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        """
        Find the innermost env where var appears.
        """
        if var in self:
            return self
        elif self.outer:
            return self.outer.find(var)


def standard_env():
    env = Env()
    math_vars = {key: value for key, value in vars(math).items() if
                 not key.startswith('__')}
    env.update(math_vars)
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        'abs': abs,
        'append': op.add,
        # TODO: modify it after apply is defined
        'apply': 'apply',
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?': op.is_,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, list),
        'map': lambda x, y: list(map(x, y)),
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env


global_env = standard_env()
