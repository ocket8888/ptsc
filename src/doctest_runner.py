#!/usr/bin/python3

if __name__ == "__main__":
	from ptsc import ast, builtins, environment, evaluator, lexer, tsobject, parser, repl, tstoken
	import doctest
	doctest.testmod(ast)
	doctest.testmod(builtins)
	doctest.testmod(environment)
	doctest.testmod(evaluator)
	doctest.testmod(lexer)
	doctest.testmod(tsobject)
	doctest.testmod(parser)
	doctest.testmod(repl)
	doctest.testmod(tstoken)
