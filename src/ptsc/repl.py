import io
import os
import typing

from . import environment
from . import evaluator
from . import lexer
from . import object as object
from . import parser

PROMPT = os.environ.get("PS2", ">> ")

def Start(In: io.TextIOWrapper, Out: io.TextIOWrapper):
	env = environment.Environment()

	while In.readable and Out.writable:
		print(PROMPT, end="\r")
		l = In.readline().lstrip(PROMPT)
		if not l:
			return

		p = parser.Parser(lexer.Lexer(l))
		program = p.ParseProgram()
		if p.Errors():
			printParserErrors(Out, p.Errors())
			continue

		evaluated = evaluator.Eval(program, env)
		if evaluated is not None:
			Out.write(evaluated.Inspect())
			Out.write('\n')


MONKEY_FACE = '''        __,__
   .--.  .-"     "-.  .--.
  / .. \/  .-. .-.  \/ .. \\
 | |  '|  /   Y   \  |'  | |
 | \   \  \ 0 | 0 /  /   / |
  \ '- ,\.-"""""""-./, -' /
   ''-' /_   ^ ^   _\ '-''
       |  \._   _./  |
       \   \ '~' /   /
        '._ '-=-' _.'
           '-----'
'''

def printParserErrors(out: io.TextIOWrapper, errors: typing.List[str]):
	out.write(MONKEY_FACE)
	out.write("Woops! We ran into some monkey business here!\n")
	out.write(" parser errors:\n")
	for msg in errors:
		out.write(f"\t{msg}\n")
