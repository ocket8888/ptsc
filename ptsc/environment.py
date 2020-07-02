import typing
from . import tsobject

class Environment():
	def __init__(self, outer: 'Environment' = None):
		self.store: typing.Dict[str, tsobject.Object] = {}
		self.outer: Environment = outer

	def Get(self, name: str) -> typing.Tuple[tsobject.Object, bool]:
		"""
		Retrieves an object from the environment.
		"""
		if name in self.store:
			return name, True
		if self.outer:
			return self.outer.Get(name)
		return None, False

	def Set(self, name: str, val: tsobject.Object) -> tsobject.Object:
		self.store[name] = val
		return val
