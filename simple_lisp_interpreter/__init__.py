# -*- coding: utf-8 -*-

import sys

from .env import global_env, Env
from .const import (
    Symbol, List, quote, if_, set_, define, lambda_, begin)
from .parser import parse, Stream, end_of_object
from .helper import to_lisp_string


class Procedure(object):

    def __init__(self, params, exp, env):
        self.params = params
        self.exp = exp
        self.env = env

    def __call__(self, *args):
        return eval_(self.exp, Env(self.params, args, self.env))


def eval_(exp, env=global_env):
    while True:
        if isinstance(exp, Symbol):
            # Variable reference
            return env.find(exp)[exp]
        elif not isinstance(exp, List):
            # Constant literal
            return exp
        elif exp[0] == quote:
            # Quotation
            _, expression = exp
            return expression
        elif exp[0] == if_:
            # Conditional situation
            _, test, conseq, alt = exp
            exp = (conseq if eval_(test, env) else alt)
        elif exp[0] == define:
            # Definition
            _, var, expression = exp
            # XXX: Let expand handle this
            # if not isinstance(var, List):
            #     env[var] = eval_(expression, env)
            # else:
            #     # eval to a lambda expression
            #     lambda_exp = [lambda_, var[1:], expression]
            #     env[var[0]] = eval_(lambda_exp, env)
            env[var] = eval_(expression, env)
            return
        elif exp[0] == set_:
            # Assignment
            _, var, expression = exp
            current_env = env.find(var)
            if not current_env:
                current_env = env
            current_env[var] = eval_(expression, env)
            return
        elif exp[0] == lambda_:
            # Procedure definition
            _, params, body = exp
            return Procedure(params, body, env)
        elif exp[0] == begin:
            for expression in exp[1: -1]:
                eval_(expression, env)
            exp = exp[-1]
        else:
            # Procedure call
            exps = [eval_(arg, env) for arg in exp]
            proc = exps.pop(0)
            if isinstance(proc, Procedure):
                exp = proc.exp
                env = Env(proc.params, exps, proc.env)
            else:
                return proc(*exps)


def schemestr(exp):
    """
    Convert a Python object back into a  Scheme-readable string

    """
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)


def repl(prompt='lisp-repl >> ', in_=Stream(sys.stdin), out=sys.stdout):
    while True:
        try:
            if prompt:
                sys.stdout.write(prompt)
                sys.stdout.flush()
            expr = parse(in_)
            if expr is end_of_object:
                return
            val = eval_(expr)
            if val and out:
                out.write(to_lisp_string(val) + '\n')
        except Exception as e:
            out.write('{}: {}\n'.format(type(e), e))


def load(filename):
    with open(filename, 'r') as file_:
        repl(None, in_=Stream(file_), out=None)
