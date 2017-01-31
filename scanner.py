class Scanner:
	"""Scans a source file to build a parse tree"""

	def __init__(self, languageVersion, skipTrivia, languageVariant=languageVariant.Standard, text=None, onError=None, start=None, length=None):
		self.pos = 0
		self.end = 0
		self.startPos = 0
		self.tokenPos = 0
		self.token = None
		self.tokenValue = ""
		self.precedingLineBreak = False
		self.hasExtendedUnicodeEscape = False
		self.tokenIsUnterminated = False
		self.setText(text, start, length)

	def setText(self, newText, start, length):
		self.text = newText if newText else ""
		self.end = len(self.text) if length == None else start+length
		self.setTextPos(start if start else 0)

