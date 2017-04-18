from enum import Enum

class Symbol:
	"""A single symbol in the parse tree"""
	def __init__(self, flags, name):
		self.flags = flags
		self.name = name
		self.declarations = None
		

class Type:
	"""A type. What did you expect?"""
	def __init__(self, checker, flags):
		self.checker = checker
		self.flags = flags
		

class Signature:
	"""Honestly? idk wtf this is"""
	def __init__(self, checker):
		self.checker = checker


class Node:
	"""A uh... Node."""
	def __init__(self, kind, pos, end):
		self.kind = kind
		self.pos = pos
		self.end = end
		self.flags = NodeFlags.none
		self.parent = None


class objectAllocator:
	"""Really dumb imho, just has a bunch of constructors."""
	
	def getNodeConstructor():
		return Node

	def getTokenConstructor():
		return Node

	def getIdentifierConstructor():
		return Node

	def getSourceFileConstructor():
		return Node

	def getSymbolConstructor():
		return Symbol

	def getTypeConstructor():
		return Type

	def getSignatureConstructor():
		return Signature	


class AssertionLevel(Enum):
	"""Specifies how strict assertions will be"""
	none = 0
	Normal = 1
	Aggressive = 2
	VeryAggressive = 3


class debug:
	"""Used to enforce assertions and cause compilation
	to fail in case of unrecoverable errors."""
	
	def __init__(self):
		self.currentAssertionLevel = AssertionLevel.none

	def shouldAssert(self, level):
		return (self.currentAssertionLevel >= level)

	def Assert(self, expression, message="", verboseDebugInfo=None):
		if not expression:
			verboseDebugString = ""
			if verboseDebugInfo:
				verboseDebugString = "\nVerboseDebugInformation: " + verboseDebugInfo()
			raise DebuggerError("Debug Failure. False expression: " + message + verboseDebugString)

	def fail(self, message):
		self.Assert(False, message)

Debug = debug()
						

def getScriptKindFromFileName(fileName):
	ext = fileName.split(".")
	ext = ext[len(ext)-1].lower()
	if ext == ".js":
		return scriptKind.JS
	elif ext == ".jsx":
		return scriptKind.JSX
	elif ext == ".ts":
		return scriptKind.TS
	elif ext == ".tsx":
		return ScriptKind.TSX
	return ScriptKind.Unknown

def ensureScriptKind(fileName, scriptKind=None):
	return getScriptKindFromFileName(fileName) if scriptKind == None else scriptKind
