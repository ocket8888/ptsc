"""
This package contains the evaluator logic for the language.

>>> TRUE.Inspect()
'true'
>>> FALSE.Inspect()
'false'
>>> NULL.Inspect()
'null'
>>> UNDEFINED.Inspect()
'undefined'
"""

import typing

from . import ast
from . import environment
from . import tsobject
from . import builtins
from . import parser, lexer

NULL = tsobject.Null()
UNDEFINED = tsobject.Object()
TRUE = tsobject.Boolean(Value=True)
FALSE = tsobject.Boolean(Value=False)

def Eval(node: ast.Node, env: environment.Environment) -> typing.Optional[tsobject.Object]:
	"""
	Evaluates any kind of node, based on its type.

	>>> evalProgram(parser.Parser(lexer.Lexer("return 10;")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("return 10; 9;")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("return 2*5; 9;")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("9; return 2*5; 9;")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("if (10>1) {if (10>1) {return 10;}; return 1;}")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("let a = 5; a;")).ParseProgram(), environment.Environment()).Value
	5
	>>> evalProgram(parser.Parser(lexer.Lexer("let a = 5*5; a;")).ParseProgram(), environment.Environment()).Value
	25
	>>> evalProgram(parser.Parser(lexer.Lexer("let a = 5; let b = a; b;")).ParseProgram(), environment.Environment()).Value
	5
	>>> evalProgram(parser.Parser(lexer.Lexer("let a = 5; let b = a; let c = a + b + 5; c;")).ParseProgram(), environment.Environment()).Value
	15
	>>> f = evalProgram(parser.Parser(lexer.Lexer("function(x) {x+2;};")).ParseProgram(), environment.Environment())
	>>> len(f.Parameters)
	1
	>>> str(f.Parameters[0])
	'x'
	>>> str(f.Body)
	'(x + 2)'
	>>> evalProgram(parser.Parser(lexer.Lexer('"Hello World!"')).ParseProgram(), environment.Environment()).Value
	'Hello World!'
	"""
	if isinstance(node, ast.Program):
		return evalProgram(node, env)

	if isinstance(node, ast.BlockStatement):
		return evalBlockStatement(node, env)

	if isinstance(node, ast.ExpressionStatement):
		return Eval(node.Expression, env)

	if isinstance(node, ast.ReturnStatement):
		val = Eval(node.ReturnValue, env)
		if isError(val):
			return val
		return tsobject.ReturnValue(Value=val)

	if isinstance(node, ast.LetStatement):
		val = Eval(node.Value, env)
		if isError(val):
			return val
		env.Set(node.Name.Value, val)

	if isinstance(node, ast.IntegerLiteral):
		return tsobject.Integer(Value=node.Value)

	if isinstance(node, ast.StringLiteral):
		return tsobject.String(Value=node.Value)

	if isinstance(node, ast.Boolean):
		return nativeBoolToBooleanObject(node.Value)

	if isinstance(node, ast.PrefixExpression):
		right = Eval(node.Right, env)
		if isError(right):
			return right
		return evalPrefixExpression(node.Operator, right)

	if isinstance(node, ast.InfixExpression):
		left = Eval(node.Left, env)
		if isError(left):
			return left

		right = Eval(node.Right, env)
		if isError(right):
			return right
		return evalInfixExpression(node.Operator, left, right)

	if isinstance(node, ast.IfExpression):
		return evalIfExpression(node, env)

	if isinstance(node, ast.Identifier):
		return evalIdentifier(node, env)

	if isinstance(node, ast.FunctionLiteral):
		return tsobject.Function(Parameters=node.Parameters, Env=env, Body=node.Body)

	if isinstance(node, ast.CallExpression):
		fn = Eval(node.Function, env)
		if isError(fn):
			return fn

		args = evalExpressions(node.Arguments, env)
		if len(args) == 1 and isError(args[0]):
			return args[0]

		return applyFunction(fn, *args)

	if isinstance(node, ast.ArrayLiteral):
		elems = evalExpressions(node.Elements, env)
		if len(elems) == 1 and isError(elems[0]):
			return elems[0]
		return tsobject.Array(Elements=elems)

	if isinstance(node, ast.IndexExpression):
		left = Eval(node.Left, env)
		if isError(left):
			return left
		index = Eval(node.Index, env)
		if isError(index):
			return index
		return evalIndexExpression(left, index)

	if isinstance(node, ast.HashLiteral):
		return evalHashLiteral(node, env)

	return None

def evalProgram(program: ast.Program, env: environment.Environment) -> tsobject.Object:
	"""
	Evaluates an entire program, with a given environment.

	>>> evalProgram(parser.Parser(lexer.Lexer("5;")).ParseProgram(), environment.Environment()).Value
	5
	>>> evalProgram(parser.Parser(lexer.Lexer("10;")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("-5;")).ParseProgram(), environment.Environment()).Value
	-5
	>>> evalProgram(parser.Parser(lexer.Lexer("-10;")).ParseProgram(), environment.Environment()).Value
	-10
	>>> evalProgram(parser.Parser(lexer.Lexer("5+5+5+5-10;")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("2*2*2*2*2;")).ParseProgram(), environment.Environment()).Value
	32
	>>> evalProgram(parser.Parser(lexer.Lexer("-50+100+-50;")).ParseProgram(), environment.Environment()).Value
	0
	>>> evalProgram(parser.Parser(lexer.Lexer("5*2 + 10;")).ParseProgram(), environment.Environment()).Value
	20
	>>> evalProgram(parser.Parser(lexer.Lexer("5+2*10;")).ParseProgram(), environment.Environment()).Value
	25
	>>> evalProgram(parser.Parser(lexer.Lexer("20+2*-10;")).ParseProgram(), environment.Environment()).Value
	0
	>>> evalProgram(parser.Parser(lexer.Lexer("50/2*2+10;")).ParseProgram(), environment.Environment()).Value
	60.0
	>>> evalProgram(parser.Parser(lexer.Lexer("2*(5+10);")).ParseProgram(), environment.Environment()).Value
	30
	>>> evalProgram(parser.Parser(lexer.Lexer("3*3*3+10;")).ParseProgram(), environment.Environment()).Value
	37
	>>> evalProgram(parser.Parser(lexer.Lexer("3*(3*3)+10;")).ParseProgram(), environment.Environment()).Value
	37
	>>> evalProgram(parser.Parser(lexer.Lexer("(5+10*2+15/3)*2+-10;")).ParseProgram(), environment.Environment()).Value
	50.0
	>>> evalProgram(parser.Parser(lexer.Lexer("")).ParseProgram(), environment.Environment())
	undefined
	"""
	res = tsobject.Object()

	for statement in program.Statements:
		res = Eval(statement, env)

		if isinstance(res, tsobject.ReturnValue):
			return res.Value
		if isinstance(res, tsobject.Error):
			return res

	return res

def evalBlockStatement(block: ast.BlockStatement, env: environment.Environment) -> tsobject.Object:
	res = tsobject.Object()

	for stmt in block.Statements:
		res = Eval(stmt, env)

		if res is not None:
			if res.Type == tsobject.ObjectType.RETURN_VALUE_OBJ or res.Type == tsobject.ObjectType.ERROR_OBJ:
				return res

	return res

def nativeBoolToBooleanObject(input: bool) -> tsobject.Boolean:
	"""
	Converts a native boolean to the REPL's boolean object.

	>>> evalProgram(parser.Parser(lexer.Lexer("true;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("false;")).ParseProgram(), environment.Environment()).Value
	False
	"""
	return TRUE if input else FALSE

def evalPrefixExpression(operator: str, right: tsobject.Object) -> tsobject.Object:
	"""
	Evaluates prefix expressions, e.g. '!true;'

	>>> evalProgram(parser.Parser(lexer.Lexer("!true;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("!false;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("!5;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("!!true;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("!!false;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("!!5;")).ParseProgram(), environment.Environment()).Value
	True
	"""
	if operator == "!":
		return evalBangOperatorExpression(right)
	if operator == "-":
		return evalMinusPrefixOperatorExpression(right)
	return newError(f"unknown operator: {operator}{right.Type}")

def evalInfixExpression(operator: str, left: tsobject.Object, right: tsobject.Object) -> tsobject.Object:
	"""
	Evaluates an infix expression.

	>>> evalProgram(parser.Parser(lexer.Lexer("1<2;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("1>2;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("1<1;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("1>1;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("1 == 1;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("1 != 1;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("1 == 2;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("1 != 2;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("true == true;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("false == false;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("true == false;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("true != false;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("false != true;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("(1 < 2) == true;")).ParseProgram(), environment.Environment()).Value
	True
	>>> evalProgram(parser.Parser(lexer.Lexer("(1 < 2) == false;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("(1 > 2) == true;")).ParseProgram(), environment.Environment()).Value
	False
	>>> evalProgram(parser.Parser(lexer.Lexer("(1 > 2) == false;")).ParseProgram(), environment.Environment()).Value
	True
	"""
	if left.Type == tsobject.ObjectType.INTEGER_OBJ and right.Type == tsobject.ObjectType.INTEGER_OBJ:
		return evalIntegerInfixExpression(operator, left, right)
	if left.Type == tsobject.ObjectType.STRING_OBJ and right.Type == tsobject.ObjectType.STRING_OBJ:
		return evalStringInfixExpression(operator, left, right)
	if operator == "==":
		return nativeBoolToBooleanObject(left == right)
	if operator == "!=":
		return nativeBoolToBooleanObject(left != right)
	if left.Type != right.Type:
		return newError(f"type mismatch: {left.Type} {operator} {right.Type}")
	return newError(f"unknown operator {left.Type} {operator} {right.Type}")

def evalBangOperatorExpression(right: tsobject.Object) -> tsobject.Object:
	if right is FALSE or right is NULL:
		return TRUE
	return FALSE

def evalMinusPrefixOperatorExpression(right: tsobject.Object) -> tsobject.Object:
	if right.Type != tsobject.ObjectType.INTEGER_OBJ:
		return newError(f"unknown operator: -{right.Type}")
	return tsobject.Integer(Value=-right.Value)

def evalIntegerInfixExpression(operator: str, left: tsobject.Object, right: tsobject.Object) -> tsobject.Object:
	lvalue, rvalue = left.Value, right.Value

	if operator == "+":
		return tsobject.Integer(Value=lvalue+rvalue)
	if operator == "-":
		return tsobject.Integer(Value=lvalue-rvalue)
	if operator == "*":
		return tsobject.Integer(Value=lvalue*rvalue)
	if operator == "/":
		return tsobject.Integer(Value=lvalue/rvalue)
	if operator == "<":
		return nativeBoolToBooleanObject(lvalue < rvalue)
	if operator == ">":
		return nativeBoolToBooleanObject(lvalue > rvalue)
	if operator == "==":
		return nativeBoolToBooleanObject(lvalue == rvalue)
	if operator == "!=":
		return nativeBoolToBooleanObject(lvalue != rvalue)
	return newError(f"unknown operator: {left.Type} {operator} {right.Type}")

def evalStringInfixExpression(operator: str, left: tsobject.Object, right: tsobject.Object) -> tsobject.Object:
	"""
	Evaluates a string infix expression, e.g. '"Hello "+"World!"'

	>>> evalProgram(parser.Parser(lexer.Lexer('"Hello "+"World!"')).ParseProgram(), environment.Environment()).Value
	'Hello World!'
	"""
	if operator != "+":
		return newError(f"unknown operator: {left.Type} {operator} {right.Type}")

	return tsobject.String(Value=left.Value + right.Value)

def evalIfExpression(ie: ast.IfExpression, env: environment.Environment) -> tsobject.Object:
	"""
	Evaluates conditionals, e.g. "if (x) {y()} else {z = z + 1;}"

	>>> evalProgram(parser.Parser(lexer.Lexer("if (true) {10}")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("if (false) {10}")).ParseProgram(), environment.Environment())
	null
	>>> evalProgram(parser.Parser(lexer.Lexer("if (1) {10}")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("if (1<2) {10};")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("if (1>2) {10};")).ParseProgram(), environment.Environment())
	null
	>>> evalProgram(parser.Parser(lexer.Lexer("if (1>2) {10} else {20}")).ParseProgram(), environment.Environment()).Value
	20
	>>> evalProgram(parser.Parser(lexer.Lexer("if (1<2) {10} else {20};")).ParseProgram(), environment.Environment()).Value
	10
	"""
	condition = Eval(ie.Condition, env)
	if isError(condition):
		return condition

	if isTruthy(condition):
		return Eval(ie.Consequence, env)
	if ie.Alternative is not None:
		return Eval(ie.Alternative, env)
	return NULL

def evalIdentifier(node: ast.Identifier, env: environment.Environment) -> tsobject.Object:
	val, ok = env.Get(node.Value)
	if ok:
		if not isinstance(val, tsobject.Object):
			raise TypeError("ayy, what?")
		return val

	return builtins.builtins.get(node.Value, newError(f"identifier not found: {node.Value}"))

def isTruthy(o: tsobject.Object) -> bool:
	if o is NULL or o is FALSE:
		return False
	return True

def newError(msg: str) -> tsobject.Error:
	return tsobject.Error(Message=msg)

def isError(o: tsobject.Object) -> bool:
	if o is not None:
		return o.Type == tsobject.ObjectType.ERROR_OBJ
	return False

def evalExpressions(exps: typing.List[ast.Expression], env: environment.Environment) -> tsobject.Object:
	result = []
	for e in exps:
		evaluated = Eval(e, env)
		if isError(evaluated):
			return [evaluated]
		result.append(evaluated)

	return result

def applyFunction(fn: tsobject.Object, *args: typing.Tuple[tsobject.Object]) -> tsobject.Object:
	"""
	Applies a function to its arguments.

	>>> evalProgram(parser.Parser(lexer.Lexer("let identity = function(x){x;}; identity(5);")).ParseProgram(), environment.Environment()).Value
	5
	>>> evalProgram(parser.Parser(lexer.Lexer("let identity = function(x){return x;}; identity(5);")).ParseProgram(), environment.Environment()).Value
	5
	>>> evalProgram(parser.Parser(lexer.Lexer("let double = function(x){return x*2;}; double(5);")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("let add = function(x, y){return x+y;}; add(5, 5);")).ParseProgram(), environment.Environment()).Value
	10
	>>> evalProgram(parser.Parser(lexer.Lexer("let add = function(x, y){return x+y;}; add(5+5, add(5,5));")).ParseProgram(), environment.Environment()).Value
	20
	>>> evalProgram(parser.Parser(lexer.Lexer("function(x){x;}(5);")).ParseProgram(), environment.Environment()).Value
	5
	>>> evalProgram(parser.Parser(lexer.Lexer('len("")')).ParseProgram(), environment.Environment())
	0
	>>> evalProgram(parser.Parser(lexer.Lexer('len("four")')).ParseProgram(), environment.Environment())
	4
	>>> evalProgram(parser.Parser(lexer.Lexer('len("hello world")')).ParseProgram(), environment.Environment())
	11
	>>> evalProgram(parser.Parser(lexer.Lexer('len(1)')).ParseProgram(), environment.Environment())
	ERROR: argument to `len` not supported, got INTEGER
	>>> evalProgram(parser.Parser(lexer.Lexer('len("one", "two")')).ParseProgram(), environment.Environment())
	ERROR: wrong number of arguments. got=2, want=1
	>>> evalProgram(parser.Parser(lexer.Lexer('len([])')).ParseProgram(), environment.Environment())
	0
	>>> evalProgram(parser.Parser(lexer.Lexer('len([1, 2, 3])')).ParseProgram(), environment.Environment())
	3
	>>> evalProgram(parser.Parser(lexer.Lexer('len([0])')).ParseProgram(), environment.Environment())
	1
	>>> evalProgram(parser.Parser(lexer.Lexer('first([1, 2, 3])')).ParseProgram(), environment.Environment())
	1
	>>> evalProgram(parser.Parser(lexer.Lexer('first([3, 2, 1])')).ParseProgram(), environment.Environment())
	3
	>>> evalProgram(parser.Parser(lexer.Lexer('first([0])')).ParseProgram(), environment.Environment())
	0
	>>> evalProgram(parser.Parser(lexer.Lexer('first([])')).ParseProgram(), environment.Environment())
	undefined
	>>> evalProgram(parser.Parser(lexer.Lexer('first([1, 2, 3], [])')).ParseProgram(), environment.Environment())
	ERROR: wrong number of arguments. got=2, want=1
	>>> evalProgram(parser.Parser(lexer.Lexer('first(1)')).ParseProgram(), environment.Environment())
	ERROR: argument to `first` must be ARRAY, got INTEGER
	"""
	if isinstance(fn, tsobject.Function):
		try:
			extendedEnv = extendFunctionEnv(fn, *args)
			return unwrapReturnValue(Eval(fn.Body, extendedEnv))
		except ValueError as e:
			return newError(str(e))

	if isinstance(fn, tsobject.Builtin):
		return fn.Fn(*args)

	return newError(f"not a function: {fn.Type}")

def extendFunctionEnv(fn: tsobject.Function, *args: typing.Tuple[tsobject.Object]) -> environment.Environment:
	"""
	Extends the execution environment of a function by adding its defined arguments to their
	specified parameter labels.

	>>> input = "let newAdder = function(x){return function(y){return x+y;};}; let addTwo=newAdder(2); addTwo(2);"
	>>> evalProgram(parser.Parser(lexer.Lexer(input)).ParseProgram(), environment.Environment()).Value
	4
	"""
	if len(args) != len(fn.Parameters):
		raise ValueError(f"Incorrect number of arguments, expected {len(fn.Parameters)}, got {len(args)}")
	env = environment.Environment(outer=fn.Env)
	for i, p in enumerate(fn.Parameters):
		env.Set(p.Value, args[i])
	return env

def unwrapReturnValue(o: tsobject.Object) -> tsobject.Object:
	if isinstance(o, tsobject.ReturnValue):
		return o.Value
	return o

def evalIndexExpression(left: tsobject.Object, index: tsobject.Object) -> tsobject.Object:
	if left.Type == tsobject.ObjectType.ARRAY_OBJ and index.Type == tsobject.ObjectType.INTEGER_OBJ:
		return evalArrayIndexExpression(left, index)
	if left.Type == tsobject.ObjectType.HASH_OBJ:
		return evalHashIndexExpression(left, index)
	return newError(f"index operator not supported: {left.Type}")

def evalArrayIndexExpression(arr: tsobject.Array, index: tsobject.Integer) -> tsobject.Object:
	if index < 0 or index > len(arr.Elements) - 1:
		return NULL
	return arr.Elements[index]

def evalHashLiteral(node: ast.HashLiteral, env: environment.Environment) -> tsobject.Object:
	pairs = {}
	for k, v in node.Pairs:
		key = Eval(k, env)
		if isError(key):
			return key

		if not isinstance(key, tsobject.Hashable):
			return newError(f"unusable as hash key: {key.Type}")

		value = Eval(v, env)
		if isError(value):
			return value

		hashed = key.HashKey()
		pairs[hashed] = tsobject.HashPair(Key=key, Value=value)
	return tsobject.Hash(Pairs=pairs)

def evalHashIndexExpression(hash: tsobject.Hash, index: tsobject.Object) -> tsobject.Object:
	if not isinstance(index, tsobject.Hashable):
		return newError(f"unusable as hash key: {index.Type}")

	key = index.HashKey()
	return hash.Pairs[key].Value if key in hash.Pairs else UNDEFINED
