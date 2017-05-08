# -*- coding: utf-8 -*-

from .env import global_env, Env
from .const import Symbol, List
from .parser import parse


class Procedure(object):

    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        return eval_(self.body, Env(self.params, args, self.env))


def eval_(exp, env=global_env):
    if isinstance(exp, Symbol):
        # Variable reference
        return env.find(exp)[exp]
    elif not isinstance(exp, List):
        # Constant literal
        return exp
    elif exp[0] == 'quote':
        # Quotation
        _, expression = exp
        return expression
    elif exp[0] == 'if':
        # Conditional situation
        _, test, conseq, alt = exp
        expression = (conseq if eval_(test, env) else alt)
        return eval_(expression, env)
    elif exp[0] == 'define':
        # Definition
        _, var, expression = exp
        env[var] = eval_(expression, env)
    elif exp[0] == 'set!':
        # Assignment
        _, var, expression = exp
        current_env = env.find(var)
        if not current_env:
            current_env = env
        current_env[var] = eval_(expression, env)
    elif exp[0] == 'lambda':
        # Procedure definition
        _, params, body = exp
        return Procedure(params, body, env)
    else:
        # Procedure call
        proc = eval_(exp[0], env)
        args = [eval_(arg, env) for arg in exp[1:]]
        return proc(*args)


def schemestr(exp):
    """
    Convert a Python object back into a  Scheme-readable string

    """
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)


def repl(prompt='lisp-repl >> '):
    while True:
        val = eval_(parse(input(prompt)))
        if val:
            print(schemestr(val))
