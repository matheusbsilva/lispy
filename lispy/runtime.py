import math
import operator as op
from collections import ChainMap
from types import MappingProxyType

from .symbol import Symbol


def eval(x, env=None):
    """
    Avalia expressão no ambiente de execução dado.
    """

    # Cria ambiente padrão, caso o usuário não passe o argumento opcional "env"
    if env is None:
        env = ChainMap({}, global_env)

    # Avalia tipos atômicos
    if isinstance(x, Symbol):
        return env[x]
    elif isinstance(x, (int, float, bool, str)):
        return x

    # Avalia formas especiais e listas
    head, *args = x

    # Comando (if <test> <then> <other>)
    # Ex: (if (even? x) (quotient x 2) x)
    if head == Symbol.IF:
        (cond, conseq, alt) = args
        exp = (conseq if eval(cond, env) else alt)
        return eval(exp, env)

    # Comando (define <symbol> <expression>)
    # Ex: (define x (+ 40 2))
    elif head == Symbol.DEFINE:
        (var, exp) = args
        result = eval(exp, env)
        env[var] = result

    # Comando (quote <expression>)
    # (quote (1 2 3))
    elif head == Symbol.QUOTE:
        return args[0]

    # Comando (let <expression> <expression>)
    # (let ((x 1) (y 2)) (+ x y))
    elif head == Symbol.LET:

        (_, defs, expr) = x
        local = ChainMap({}, env)

        for i in defs:
            eval([Symbol.DEFINE, i[0], i[1]], local)

        return eval(expr, local)

    # Comando (lambda <vars> <body>)
    # (lambda (x) (+ x 1))
    elif head == Symbol.LAMBDA:
          (var, body) = args
  
          if not isinstance(var, list):
              var = [var]
  
          if not all(map(lambda params: isinstance(params, Symbol), var)):
              raise TypeError('Invalid parameters!')
  
          def lamb(*args):
              local = env.new_child(
                  {Symbol(sym): eval(v, env) for sym, v in zip(var, args)}
              )
              return eval(body, local)
  
          return lamb

    # Lista/chamada de funções
    # (sqrt 4)
    else:
        proc = eval(head, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)

#
# Cria ambiente de execução.
#
def env(*args, **kwargs):
    """
    Retorna um ambiente de execução que pode ser aproveitado pela função
    eval().

    Aceita um dicionário como argumento posicional opcional. Argumentos nomeados
    são salvos como atribuições de variáveis.

    Ambiente padrão
    >>> env()
    {...}

    Acrescenta algumas variáveis explicitamente
    >>> env(x=1, y=2)
    {x: 1, y: 2, ...}

    Passa um dicionário com variáveis adicionais
    >>> d = {Symbol('x'): 1, Symbol('y'): 2}
    >>> env(d)
    {x: 1, y: 2, ...}
    """

    kwargs = {Symbol(k): v for k, v in kwargs.items()}
    if len(args) > 1:
        raise TypeError('accepts zero or one positional arguments')
    elif len(args):
        if any(not isinstance(x, Symbol) for x in args[0]):
            raise ValueError('keys in a environment must be Symbols')
        args[0].update(kwargs)
        return ChainMap(args[0], global_env)
    return ChainMap(kwargs, global_env)


def _make_global_env():
    """
    Retorna dicionário fechado para escrita relacionando o nome das variáveis aos
    respectivos valores.
    """

    dic = {
        **vars(math), # sin, cos, sqrt, pi, ...
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: head,
        'cdr':     lambda x: x[1:],
        'cons':    lambda x, y: [x] + y,
        'eq?':     op.is_,
        'expt':    pow,
        'equal?':  op.eq,
        'even?':   lambda x: x % 2 == 0,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x, list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, (float, int)),
        'odd?':   lambda x: x % 2 == 1,
        'print':   print,
        'procedure?': callable,
        'quotient': op.floordiv,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    }
    return MappingProxyType({Symbol(k): v for k, v in dic.items()})

global_env = _make_global_env()

