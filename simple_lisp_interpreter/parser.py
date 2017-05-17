# -*- coding: utf-8 -*-

import re

from .const import (
    Symbol, sym, quote, quasiquote, unquote, unquote_splicing,
    if_, set_, define, lambda_, begin, define_macro, let,
    cons_, append
)
from .helper import require
from .env import cons, macro_table, is_pair


end_of_object = Symbol('#end-of-object')

quotes = {
    "'": quote,
    '`': quasiquote,
    ',': unquote,
    ',@': unquote_splicing,
}


def atom(token):
    if token == '#t':
        # boolean True
        return True
    elif token == '#f':
        # boolean False
        return False
    elif token[0] == '"' and token[-1] == '"':
        return token[1: -1]
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            try:
                return complex(token.replace('i', 'j', 1))
            except ValueError:
                return sym(token)


class Stream(object):
    """
    Input port, also known as file objects or streams.
    Retains a line of chars
    """

    # tokenizer
    tknizer = r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)'''

    def __init__(self, file_):
        self.file_ = file_
        self.line = ''

    def next_token(self):
        """
        Return the next token, reading new text into line buffer if needed.

        """
        while True:
            if self.line == '':
                self.line = self.file_.readline()
            if self.line == '':
                return end_of_object
            token, self.line = re.match(self.tknizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token


def readchar(stream):
    """Read the next character from a stream"""
    if stream.line != '':
        ch, stream.line = stream.line[0], stream.line[1:]
        return ch
    else:
        return stream.file_.read(1) or end_of_object


def read(stream):
    """Read a Scheme expression from a stream"""
    def read_ahead(token):
        if token == '(':
            expr = []
            while True:
                token = stream.next_token()
                if token == ')':
                    return expr
                else:
                    expr.append(read_ahead(token))
        elif token == ')':
            raise SyntaxError('Unexpected )')
        elif token in quotes:
            return [quotes[token], read(stream)]
        elif token is end_of_object:
            raise SyntaxError('Unexpected EOF in list')
        else:
            return atom(token)

    token = stream.next_token()
    if token == end_of_object:
        return end_of_object
    else:
        return read_ahead(token)


def read_from_tokens(tokens):
    """
    read a sequence of tokens, and return nested list of expression

    """
    if len(tokens) == 0:
        raise SyntaxError('Unexpected EOF while reading')

    token = tokens.pop(0)
    if token == '(':
        ret = []
        while tokens[0] != ')':
            ret.append(read_from_tokens(tokens))
        tokens.pop(0)
        return ret
    elif token == ')':
        raise SyntaxError('Unexpected )')
    else:
        return atom(token)


def expand(exp, toplevel=False):
    """
    Walk tree of exp, making optimizations/fixes,
    raise SyntaxError if syntax is incorrect.
    """
    require(exp, exp != [] and exp != ())

    if not isinstance(exp, (list, tuple)):
        return exp
    elif exp[0] == quote:
        # Quotation: (quote exp)
        require(exp, len(exp) == 2)
        return exp
    elif exp[0] == if_:
        # Conditional situation: set alt to None if not provided
        # (if test cons) => (if test cons None)
        if len(exp) == 3:
            exp = exp + [None]
        require(exp, len(exp) == 4)
        return list(map(expand, exp))
    elif exp[0] == set_:
        require(exp, len(exp) == 3)
        var = exp[1]
        require(exp, isinstance(var, (str, Symbol)),
                'set! can only work with symbol')
        if not isinstance(var, Symbol):
            var = Symbol(var)
        return [set_, var, expand(exp[2])]
    elif exp[0] == define or exp[0] == define_macro:
        require(exp, len(exp) >= 3)
        def_, var, body = exp[0], exp[1], exp[2:]
        if isinstance(var, list) and var:
            # (define (f args) body) => (define f (lambda (args) body))
            f, args = var[0], var[1:]
            return expand([def_, f, [lambda_, args] + body])
        else:
            require(exp, len(exp) == 3)
            require(exp, isinstance(var, (str, Symbol)),
                    'define can only work with symbol')
            if not isinstance(var, Symbol):
                var = Symbol(var)
            expression = expand(exp[2])
            if exp[0] == define_macro:
                # Check define-macro validation
                require(exp, toplevel,
                        'define-macro only allowed at top level')
                from __init__ import eval_
                proc = eval_(expression)
                require(exp, callable(proc), 'macro must be a procedure')
                macro_table[var] = proc
                return
            return [define, var, expression]
    elif exp[0] == begin:
        # return None if exp is (begin)
        if len(exp) > 1:
            return [expand(x, toplevel) for x in exp]
    elif exp[0] == lambda_:
        # (lambda (x) e1 e2) => (lambda (x) (begin e1 e2)
        require(exp, len(exp) >= 3)
        vars_, body = exp[1], exp[2:]
        valid_lambda_vars = (
            (isinstance(vars_, (list, tuple)) and
             all(isinstance(v, (str, Symbol)) for v in vars_)) or
            isinstance(vars_, (str, Symbol)))
        require(exp, valid_lambda_vars, 'illegal lambda argument list')
        expression = body[0] if len(body) == 1 else [begin] + body
        return [lambda_, vars_, expand(expression)]
    elif exp[0] == quasiquote:
        # `exp => expand_quasiquote(exp)
        require(exp, len(exp) == 2)
        return expand_quasiquote(exp[1])
    elif exp[0] in macro_table:
        # (m args...) and m in macro_table
        # macro expand if m is a macro
        return expand(macro_table[exp[0]](*exp[1:]), toplevel)
    else:
        return list(map(expand, exp))


def expand_quasiquote(exp):
    """
    Expand:
        `exp => 'exp
        `,exp => exp
        `(,@exp, y) => (append exp y)

    """
    if not is_pair(exp):
        return [quote, exp]
    require(exp, exp[0] is not unquote_splicing, "can't splice here")
    if exp[0] is unquote:
        require(exp, len(exp) == 2)
        return exp[1]
    elif is_pair(exp[0]) and exp[0][0] is unquote_splicing:
        require(exp[0], len(exp[0]) == 2)
        return [append, exp[0][1], expand_quasiquote(exp[1:])]
    else:
        return [cons_, expand_quasiquote(exp[0]), expand_quasiquote(exp[1:])]


def parse(program):
    """
    Read a Scheme expression from string and return nested token.

    :param program: A Stream instance for parsing
    """
    return expand(read(program), toplevel=True)


def let_macro(*args):
    exp = cons(let, args)
    require(exp, len(args) > 1)
    bindings, body = args[0], args[1:]
    require(exp, isinstance(bindings, (list, tuple)),
            'bindings of let macros should be list')
    binding_valid = all(isinstance(b, (list, tuple)) and len(b) == 2 and
                        isinstance(b[0], (str, Symbol)) for b in bindings)
    require(exp, binding_valid, 'illegal binding list')
    vars_, vals = zip(*bindings)
    return [[lambda_, list(vars_)] + list(map(expand, body))] + \
        list(map(expand, vals))


macro_table[let] = let_macro
