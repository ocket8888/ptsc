import typing

from . import ast
from . import environment
from . import tsobject
from . import builtins

NULL = tsobject.Null()
UNDEFINED = tsobject.Object()
TRUE = tsobject.Boolean(Value=True)
FALSE = tsobject.Boolean(Value=False)

def Eval(node: ast.Node, env: environment.Environment) -> typing.Optional[tsobject.Object]:
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

		return applyFunction(fn, args)

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
	return TRUE if input else FALSE

def evalPrefixExpression(operator: str, right: tsobject.Object) -> tsobject.Object:
	if operator == "!":
		return evalBangOperatorExpression(right)
	if operator == "-":
		return evalMinusPrefixOperatorExpression(right)
	return newError(f"unknown operator: {operator}{right.Type}")

def evalInfixExpression(operator: str, left: tsobject.Object, right: tsobject.Object) -> tsobject.Object:
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
	if operator != "+":
		return newError(f"unknown operator: {left.Type} {operator} {right.Type}")

	return tsobject.String(Value=left.Value + right.Value)

def evalIfExpression(ie: ast.IfExpression, env: environment.Environment) -> tsobject.Object:
	condition = Eval(ie.Condition)
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
	if isinstance(fn, tsobject.Function):
		extendedEnv = extendFunctionEnv(fn, *args)
		return unwrapReturnValue(Eval(fn.Body, extendedEnv))

	if isinstance(fn, tsobject.Builtin):
		return fn.Fn(*args)

	return newError(f"not a function: {fn.Type}")

def extendFunctionEnv(fn: tsobject.Function, *args: typing.Tuple[tsobject.Object]) -> environment.Environment:
	env = environment.Environment(outer=fn.Env)
	for i, p in range(fn.Parameters):
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
