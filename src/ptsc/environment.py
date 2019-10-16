import typing
from . import object as obj

class Environment():
	def __init__(self, outer: 'Environment' = None):
		self.store: typing.Dict[str, obj.Object] = {}
		self.outer: Environment = outer

	def Get(self, name: str) -> typing.Tuple[obj.Object, bool]:
		if name in self.store:
			return name, True
		if self.outer:
			return self.outer.Get(name)
		return None, False

	def Set(self, name: str, val: obj.Object) -> obj.Object:
		self.store[name] = val
		return val
