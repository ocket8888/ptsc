from . import tstoken

class Lexer():
	def __init__(self, input: str):
		self.input = input
		self.position = 0
		self.readPosition = 0
		self.ch = ''
		self.readChar()

	def readChar(self):
		if self.readPosition >= len(self.input):
			self.ch = str(b'\x00')
		else:
			self.ch = self.input[self.readPosition]
		self.position = self.readPosition
		self.readPosition += 1

	def skipWhitespace(self):
		while self.ch in ' \t\n\r':
			self.readChar()

	def peekChar(self) -> str:
		if self.readPosition >= len(self.input):
			return str(b'\x00')
		return self.input[self.readPosition]

	def readIdentifier(self) -> str:
		pos = self.position
		while self.isLetter(self.ch):
			self.readChar()
		return self.input[pos:self.position]

	def readNumber(self) -> str:
		pos = self.position
		while self.isDigit(self.ch):
			self.readChar()
		return self.input[pos:self.position]

	def readString(self) -> str:
		pos = self.position + 1
		while True:
			self.readChar()
			if self.ch == '"' or self.ch == str(b'\x00'):
				break
		return self.input[pos:self.position]

	@staticmethod
	def isLetter(ch: str) -> bool:
		char = ord(ch)
		return ord('a') <= char and char <= ord('z') or ord('A') <= char and char <= ord('Z') or ch == '_'

	@staticmethod
	def isDigit(ch: str) -> bool:
		return ord('0') <= ord(ch) and ord(ch) <= ord('9')

	def NextToken(self) -> tstoken.Token:
		self.skipWhitespace()

		tok = tstoken.Token()
		if self.ch == '=':
			if self.peekChar() == '=':
				ch = self.ch
				self.readChar()
				literal = ch + self.ch
				tok = tstoken.Token(Type=tstoken.TokenType.EQ, Literal=literal)
			else:
				tok = newToken(tstoken.TokenType.ASSIGN, self.ch)
		elif self.ch == '+':
			tok = newToken(tstoken.TokenType.PLUS, self.ch)
		elif self.ch == '-':
			tok = newToken(tstoken.TokenType.MINUS, self.ch)
		elif self.ch == '!':
			if self.peekChar() == '=':
				ch = self.ch
				self.readChar()
				literal = ch + self.ch
				tok = tstoken.Token(Type=tstoken.TokenType.NOT_EQ, Literal=literal)
			else:
				tok = newToken(tstoken.TokenType.BANG, self.ch)
		elif self.ch == '/':
			tok = newToken(tstoken.TokenType.SLASH, self.ch)
		elif self.ch == '*':
			tok = newToken(tstoken.TokenType.ASTERISK, self.ch)
		elif self.ch == '<':
			tok = newToken(tstoken.TokenType.LT, self.ch)
		elif self.ch == '>':
			tok = newToken(tstoken.TokenType.GT, self.ch)
		elif self.ch == ';':
			tok = newToken(tstoken.TokenType.SEMICOLON, self.ch)
		elif self.ch == ':':
			tok = newToken(tstoken.TokenType.COLON, self.ch)
		elif self.ch == ',':
			tok = newToken(tstoken.TokenType.COMMA, self.ch)
		elif self.ch == '{':
			tok = newToken(tstoken.TokenType.LBRACE, self.ch)
		elif self.ch == '}':
			tok = newToken(tstoken.TokenType.RBRACE, self.ch)
		elif self.ch == '(':
			tok = newToken(tstoken.TokenType.LPAREN, self.ch)
		elif self.ch == ')':
			tok = newToken(tstoken.TokenType.RPAREN, self.ch)
		elif self.ch == '"':
			tok = tstoken.Token(Type=tstoken.TokenType.STRING, Literal=self.readString())
		elif self.ch == '[':
			tok = newToken(tstoken.TokenType.LBRACKET, self.ch)
		elif self.ch == ']':
			tok = newToken(tstoken.TokenType.RBRACKET, self.ch)
		elif self.ch == str(b'\x00'):
			tok = tstoken.Token(Type=tstoken.TokenType.EOF, Literal="")
		else:
			if self.isLetter(self.ch):
				lit = self.readIdentifier()
				return tstoken.Token(Type=tstoken.lookupIdent(lit), Literal=lit)
			elif self.isDigit(self.ch):
				lit = self.readNumber()
				return tstoken.Token(Type=tstoken.TokenType.INT, Literal=lit)
			else:
				tok = newToken(tstoken.TokenType.ILLEGAL, self.ch)

		self.readChar()
		return tok

def newToken(tstokenType: tstoken.TokenType, ch: str) -> tstoken.Token:
	return tstoken.Token(Type=tstokenType, Literal=ch)
