import enum
import typing

from . import ast
from . import environment

class BuiltinFunction():
	pass

class ObjectType(enum.Enum):
	NULL_OBJ = "NULL"
	UNDEFINED_OBJ = "UNDEFINED"
	ERROR_OBJ = "ERROR"
	INTEGER_OBJ = "INTEGER"
	BOOLEAN_OBJ = "BOOLEAN"
	STRING_OBJ = "STRING"
	RETURN_VALUE_OBJ = "RETURN_VALUE"
	FUNCTION_OBJ = "FUNCTION"
	BUILTIN_OBJ = "BUILTIN"
	ARRAY_OBJ = "ARRAY"
	HASH_OBJ = "HASH"

	def __str__(self) -> str:
		return self.value

class Object():
	def __init__(self, *args, Type: ObjectType = ObjectType.UNDEFINED_OBJ, **kwargs):
		super().__init__(*args, **kwargs)
		self.Type = Type

	def Inspect(self) -> str:
		return "undefined"

	def __repr__(self) -> str:
		return self.Inspect()

class HashKey():
	def __init__(self, *args, Type: ObjectType = ObjectType.UNDEFINED_OBJ, Value: int = 0, **kwargs):
		super().__init__(*args, **kwargs)
		self.Type = Type
		self.Value = Value

class Integer(Object):
	def __init__(self, *args, Value: int = 0, **kwargs):
		super().__init__(*args, Type=ObjectType.INTEGER_OBJ, **kwargs)
		self.Value = Value

	def Inspect(self) -> str:
		return str(self.Value)

	def HashKey(self) -> HashKey:
		return self.Value

class Boolean(Object):
	def __init__(self, *args, Value: bool = False, **kwargs):
		super().__init__(*args, Type=ObjectType.BOOLEAN_OBJ, **kwargs)
		self.Value = Value

	def Inspect(self) -> str:
		return str(self.Value).lower()

	def HashKey(self) -> HashKey:
		return hash(self.Value)

class Null(Object):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, Type=ObjectType.NULL_OBJ, **kwargs)

	def Inspect(self) -> str:
		return "null"

	def __repr__(self) -> str:
		return "null"

class ReturnValue(Object):
	def __init__(self, *args, Value: Object = None, **kwargs):
		super().__init__(*args, Type=ObjectType.RETURN_VALUE_OBJ, **kwargs)
		self.Value = Value if Value else Object()

	def Inspect(self) -> str:
		return self.Value.Inspect()

class Error(Object):
	def __init__(self, *args, Message: str = "", **kwargs):
		super().__init__(*args, Type=ObjectType.ERROR_OBJ, **kwargs)
		self.Message = Message

	def Inspect(self) -> str:
		return f"ERROR: {self.Message}"

class Function(Object):
	def __init__(self, *args, Parameters: typing.List[ast.Identifier] = None, Body: ast.BlockStatement = None, Env = None, **kwargs):
		super().__init__(*args, Type=ObjectType.FUNCTION_OBJ, **kwargs)
		self.Parameters = Parameters if Parameters else []
		self.Body = Body if Body else ast.BlockStatement()
		self.Env = Env if Env else environment.Environment()

	def Inspect(self) -> str:
		return f"function({', '.join(str(p) for p in self.Parameters)}) {{\n{self.Body}\n}}"

class String(Object):
	def __init__(self, *args, Value: str = "", **kwargs):
		super().__init__(*args, Type=ObjectType.STRING_OBJ, **kwargs)
		self.Value = Value

	def Inspect(self) -> str:
		return self.Value

	def HashKey(self) -> HashKey:
		return hash(self.Value)

class Builtin(Object):
	def __init__(self, *args, Fn: BuiltinFunction = None, **kwargs):
		super().__init__(*args, Type=ObjectType.BUILTIN_OBJ, **kwargs)
		self.Fn = Fn if Fn else BuiltinFunction()

	def Inspect(self) -> str:
		return "builtin function"

class Array(Object):
	def __init__(self, *args, Elements: typing.List[Object] = None, **kwargs):
		super().__init__(*args, Type=ObjectType.ARRAY_OBJ, **kwargs)
		self.Elements = Elements if Elements else []

	def Inspect(self) -> str:
		return f"[{', '.join(str(e) for e in self.Elements)}]"

HashPair = typing.NamedTuple('HashPair', [('Key', Object), ('Value', Object)])

class Hash(Object):
	def __init__(self, *args, Pairs: typing.Dict[HashKey, HashPair] = None, **kwargs):
		super().__init__(*args, Type=ObjectType.HASH_OBJ, **kwargs)
		self.Pairs = Pairs if Pairs else {}

	def Inspect(self) -> str:
		pairs = ', '.join(': '.join((k.Inspect(),v.Inspect())) for k, v in self.Pairs.values())
		return f"{{{pairs}}}"
