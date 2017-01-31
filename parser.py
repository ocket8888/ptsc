class Parser:
	"""The actual entire parser"""
	
	def __init__(self):
		print("testquest")

	def initializeState(self, fileName, _sourceText, languageVersion, _syntaxCursor, scriptKind):
		pass

	def parseSourceFile(self, fileName, _sourceText, languageVersion, _syntaxCursor, setParentNodes=None, scriptKind=None):
		scriptKind = ensureScriptKind(fileName, scriptKind)
		
		

def createSourceFile(fileName, sourceText, languageVersion, setParentNodes=False, scriptKind=None):
	performance.mark("beforeParse")
	result = Parser.parseSourceFile(fileName, sourceText, languageVersion, None, setParentNodes, scriptKind)
	performance.mark("afterParse")
	performance.measure("Parse", "beforeParse", "afterParse")
	return result