
Number = (int, float)

List = (list, tuple)


class Symbol(str):
    pass


def sym(s, symbol_table={}):
    """
    Find or create unique Symbol entry for str s in symbol table.

    """
    if s not in symbol_table:
        symbol_table[s] = Symbol(s)
    return symbol_table[s]


_predefine_symbols = ['quote', 'if', 'set!', 'define', 'lambda',
                      'begin', 'define-macro', 'quosiquote',
                      'unquote', 'unquote-splicing',
                      'append', 'cons', 'let']

quote, if_, set_, define, lambda_, begin, define_macro = map(
    sym, _predefine_symbols[: 7])

quasiquote, unquote, unquote_splicing = map(
    sym, _predefine_symbols[7:10])

append, cons_, let = map(sym, _predefine_symbols[10:])

del(_predefine_symbols)
