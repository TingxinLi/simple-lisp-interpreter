# -*- coding: utf-8 -*-

from .const import Symbol


def tokenize(chars):
    """
    Convert a string of codes into a list of tokens

    """
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def atom(token):
    """"
    Atomize single token: numbers -> numbers, else -> symbol

    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def read_from_tokens(tokens):
    """
    Read a sequence of tokens, and return nested list of expression
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


def parse(program):
    """
    Read a Scheme expression from string and return nested token.

    """
    return read_from_tokens(tokenize(program))
