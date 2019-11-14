from lark import Lark, InlineTransformer
from pathlib import Path

from .runtime import Symbol


class LispTransformer(InlineTransformer):

    def start(self, *args):
        return [Symbol.BEGIN, *args]

    def number(self, token):
        return float(token)

    def boolean(self, value):
        if(value == '#t'):
            return True
        elif(value == '#f'):
            return False

    def string(self, value):
        return str(eval(value))

    def symbol(self, value):
        return Symbol(value)

    def lista(self, *expr):
        return list(expr)

    def quote(self, expr):
        return [Symbol.QUOTE, expr]

    def infix(self, left, op, right):
        return [op, left, right]

    def assign(self, var, value):
        return [Symbol(var), value]

    def let_extension(self, *args):
        *assigns, expr = args
        return [Symbol.LET, assigns, expr]

def parse(src: str):
    """
    Compila string de entrada e retorna a S-expression equivalente.
    """
    return parser.parse(src)


def _make_grammar():
    """
    Retorna uma gramática do Lark inicializada.
    """

    path = Path(__file__).parent / 'grammar.lark'
    with open(path) as fd:
        grammar = Lark(fd, parser='lalr', transformer=LispTransformer())
    return grammar

parser = _make_grammar()