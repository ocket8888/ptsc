from . import token

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

	def NextToken(self) -> token.Token:
		self.skipWhitespace()

		tok = token.Token()
		if self.ch == '=':
			if self.peekChar() == '=':
				ch = self.ch
				self.readChar()
				literal = ch + self.ch
				tok = token.Token(Type=token.TokenType.EQ, Literal=literal)
			else:
				tok = newToken(token.TokenType.ASSIGN, self.ch)
		elif self.ch == '+':
			tok = newToken(token.TokenType.PLUS, self.ch)
		elif self.ch == '-':
			tok = newToken(token.TokenType.MINUS, self.ch)
		elif self.ch == '!':
			if self.peekChar() == '=':
				ch = self.ch
				self.readChar()
				literal = ch + self.ch
				tok = token.Token(Type=token.TokenType.NOT_EQ, Literal=literal)
			else:
				tok = newToken(token.TokenType.BANG, self.ch)
		elif self.ch == '/':
			tok = newToken(token.TokenType.SLASH, self.ch)
		elif self.ch == '*':
			tok = newToken(token.TokenType.ASTERISK, self.ch)
		elif self.ch == '<':
			tok = newToken(token.TokenType.LT, self.ch)
		elif self.ch == '>':
			tok = newToken(token.TokenType.GT, self.ch)
		elif self.ch == ';':
			tok = newToken(token.TokenType.SEMICOLON, self.ch)
		elif self.ch == ':':
			tok = newToken(token.TokenType.COLON, self.ch)
		elif self.ch == ',':
			tok = newToken(token.TokenType.COMMA, self.ch)
		elif self.ch == '{':
			tok = newToken(token.TokenType.LBRACE, self.ch)
		elif self.ch == '}':
			tok = newToken(token.TokenType.RBRACE, self.ch)
		elif self.ch == '(':
			tok = newToken(token.TokenType.LPAREN, self.ch)
		elif self.ch == ')':
			tok = newToken(token.TokenType.RPAREN, self.ch)
		elif self.ch == '"':
			tok = token.Token(Type=token.TokenType.STRING, Literal=self.readString())
		elif self.ch == '[':
			tok = newToken(token.TokenType.LBRACKET, self.ch)
		elif self.ch == ']':
			tok = newToken(token.TokenType.RBRACKET, self.ch)
		elif self.ch == str(b'\x00'):
			tok = token.Token(Type=token.TokenType.EOF, Literal="")
		else:
			if self.isLetter(self.ch):
				lit = self.readIdentifier()
				return token.Token(Type=token.lookupIdent(lit), Literal=lit)
			elif self.isDigit(self.ch):
				lit = self.readNumber()
				return token.Token(Type=token.TokenType.INT, Literal=lit)
			else:
				tok = newToken(token.TokenType.ILLEGAL, self.ch)

		self.readChar()
		return tok

def newToken(tokenType: token.TokenType, ch: str) -> token.Token:
	return token.Token(Type=tokenType, Literal=ch)
