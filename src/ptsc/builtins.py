from . import object as obj
from . import evaluator

def lenFunc(*args) -> obj.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")

	arg = args[0]
	if isinstance(arg, obj.Array):
		return obj.Integer(Value=len(arg.Elements))
	if isinstance(arg, obj.String):
		return obj.Integer(Value=len(arg.Value))
	return evaluator.newError(f"argument to `len` not supported, got {arg.Type}")

def putsFunc(*args) -> obj.Object:
	for arg in args:
		print(arg.Inspect())
	return evaluator.UNDEFINED

def firstFunc(*args) -> obj.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")

	arg = args[0]
	if arg.Type != obj.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"argument to `first` must be ARRAY, got {arg.Type}")

	if len(arg.Elements) > 0:
		return arg.Elements[0]
	return evaluator.UNDEFINED

def lastFunc(*args) -> obj.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")

	arg = args[0]
	if arg.Type != obj.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"argument to `last` must be ARRAY, got {arg.Type}")

	if len(arg.Elements) > 0:
		return arg.Elements[-1]
	return evaluator.UNDEFINED

def restFunc(*args) -> obj.Object:
	if len(args) != 1:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=1")
	arg = args[0]
	if arg.Type != obj.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"argument to `rest` must be ARRAY, got {arg.Type}")
	if len(arg) > 1:
		return arg[1:]
	return obj.Array() if len(arg) == 1 else evaluator.UNDEFINED

def pushFunc(*args) -> obj.Object:
	if len(args) != 2:
		return evaluator.newError(f"wrong number of arguments. got={len(args)}, want=2")

	arr, item = args[0], args[1]
	if arr.Type != obj.ObjectType.ARRAY_OBJ:
		return evaluator.newError(f"first argument to `push` must be ARRAY, got {arr.Type}")

	arr = arr.Elements
	arr.append(item)
	return obj.Array(Elements=arr)

builtins = {
	"len": lenFunc,
	"puts": putsFunc,
	"first": firstFunc,
	"last": lastFunc,
	"rest": restFunc,
	"push": pushFunc
}