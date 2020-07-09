from . import tsobject
from . import evaluator

def lenFunc(*args) -> tsobject.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")

	arg = args[0]
	if isinstance(arg, tsobject.Array):
		return tsobject.Integer(Value=len(arg.Elements))
	if isinstance(arg, tsobject.String):
		return tsobject.Integer(Value=len(arg.Value))
	return evaluator.newError(f"argument to `len` not supported, got {arg.Type}")

def putsFunc(*args) -> tsobject.Object:
	for arg in args:
		print(arg.Inspect())
	return evaluator.UNDEFINED

def firstFunc(*args) -> tsobject.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")

	arg = args[0]
	if arg.Type != tsobject.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"argument to `first` must be ARRAY, got {arg.Type}")

	if len(arg.Elements) > 0:
		return arg.Elements[0]
	return evaluator.UNDEFINED

def lastFunc(*args) -> tsobject.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")

	arg = args[0]
	if arg.Type != tsobject.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"argument to `last` must be ARRAY, got {arg.Type}")

	if len(arg.Elements) > 0:
		return arg.Elements[-1]
	return evaluator.UNDEFINED

def restFunc(*args) -> tsobject.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")
	arg = args[0]
	if arg.Type != tsobject.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"argument to `rest` must be ARRAY, got {arg.Type}")
	if len(arg.Elements) > 1:
		return tsobject.Array(Elements=arg.Elements[1:])
	return tsobject.Array() if len(arg.Elements) == 1 else evaluator.UNDEFINED

def pushFunc(*args) -> tsobject.Object:
	if len(args) != 2:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=2")

	arr, item = args[0], args[1]
	if arr.Type != tsobject.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"first argument to `push` must be ARRAY, got {arr.Type}")

	arr = arr.Elements
	arr.append(item)
	return tsobject.Array(Elements=arr)

builtins = {
	"len": tsobject.Builtin(Fn=lenFunc),
	"puts": tsobject.Builtin(Fn=putsFunc),
	"first": tsobject.Builtin(Fn=firstFunc),
	"last": tsobject.Builtin(Fn=lastFunc),
	"rest": tsobject.Builtin(Fn=restFunc),
	"push": tsobject.Builtin(Fn=pushFunc)
}
