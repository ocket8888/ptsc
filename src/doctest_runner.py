#!/usr/bin/python

if __name__ == "__main__":
	from ptsc import ast, builtins, environment, evaluator, lexer, object as obj, parser, repl, token
	import doctest
	doctest.testmod(ast)
	doctest.testmod(builtins)
	doctest.testmod(environment)
	doctest.testmod(evaluator)
	doctest.testmod(lexer)
	doctest.testmod(obj)
	doctest.testmod(parser)
	doctest.testmod(repl)
	doctest.testmod(token)
