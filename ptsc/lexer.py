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
		"""
		Parses the next token in the input stream and returns the parsed token.

		>>> ipt = '''let five = 5;\
		let ten = 10;\
		let add = function(x, y) {\
			x + y;\
		};\
		let result = add(five, ten);\
		!-/*5;\
		5 < 10 > 5;\
		if (5 < 10) {\
			return true;\
		} else {\
			return false;\
		}\
		10 == 10;\
		10 != 9;\
		"foobar"\
		"foo bar"\
		[1, 2];\
		{"foo": "bar"}'''
		>>> l = Lexer(ipt)
		>>> l.NextToken()
		Token(Type='TokenType.LET', Literal='let')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='five')
		>>> l.NextToken()
		Token(Type='TokenType.ASSIGN', Literal='=')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='5')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.LET', Literal='let')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='ten')
		>>> l.NextToken()
		Token(Type='TokenType.ASSIGN', Literal='=')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='10')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.LET', Literal='let')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='add')
		>>> l.NextToken()
		Token(Type='TokenType.ASSIGN', Literal='=')
		>>> l.NextToken()
		Token(Type='TokenType.FUNCTION', Literal='function')
		>>> l.NextToken()
		Token(Type='TokenType.LPAREN', Literal='(')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='x')
		>>> l.NextToken()
		Token(Type='TokenType.COMMA', Literal=',')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='y')
		>>> l.NextToken()
		Token(Type='TokenType.RPAREN', Literal=')')
		>>> l.NextToken()
		Token(Type='TokenType.LBRACE', Literal='{')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='x')
		>>> l.NextToken()
		Token(Type='TokenType.PLUS', Literal='+')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='y')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.RBRACE', Literal='}')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.LET', Literal='let')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='result')
		>>> l.NextToken()
		Token(Type='TokenType.ASSIGN', Literal='=')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='add')
		>>> l.NextToken()
		Token(Type='TokenType.LPAREN', Literal='(')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='five')
		>>> l.NextToken()
		Token(Type='TokenType.COMMA', Literal=',')
		>>> l.NextToken()
		Token(Type='TokenType.IDENT', Literal='ten')
		>>> l.NextToken()
		Token(Type='TokenType.RPAREN', Literal=')')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.BANG', Literal='!')
		>>> l.NextToken()
		Token(Type='TokenType.MINUS', Literal='-')
		>>> l.NextToken()
		Token(Type='TokenType.SLASH', Literal='/')
		>>> l.NextToken()
		Token(Type='TokenType.ASTERISK', Literal='*')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='5')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='5')
		>>> l.NextToken()
		Token(Type='TokenType.LT', Literal='<')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='10')
		>>> l.NextToken()
		Token(Type='TokenType.GT', Literal='>')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='5')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.IF', Literal='if')
		>>> l.NextToken()
		Token(Type='TokenType.LPAREN', Literal='(')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='5')
		>>> l.NextToken()
		Token(Type='TokenType.LT', Literal='<')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='10')
		>>> l.NextToken()
		Token(Type='TokenType.RPAREN', Literal=')')
		>>> l.NextToken()
		Token(Type='TokenType.LBRACE', Literal='{')
		>>> l.NextToken()
		Token(Type='TokenType.RETURN', Literal='return')
		>>> l.NextToken()
		Token(Type='TokenType.TRUE', Literal='true')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.RBRACE', Literal='}')
		>>> l.NextToken()
		Token(Type='TokenType.ELSE', Literal='else')
		>>> l.NextToken()
		Token(Type='TokenType.LBRACE', Literal='{')
		>>> l.NextToken()
		Token(Type='TokenType.RETURN', Literal='return')
		>>> l.NextToken()
		Token(Type='TokenType.FALSE', Literal='false')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.RBRACE', Literal='}')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='10')
		>>> l.NextToken()
		Token(Type='TokenType.EQ', Literal='==')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='10')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='10')
		>>> l.NextToken()
		Token(Type='TokenType.NOT_EQ', Literal='!=')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='9')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.STRING', Literal='foobar')
		>>> l.NextToken()
		Token(Type='TokenType.STRING', Literal='foo bar')
		>>> l.NextToken()
		Token(Type='TokenType.LBRACKET', Literal='[')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='1')
		>>> l.NextToken()
		Token(Type='TokenType.COMMA', Literal=',')
		>>> l.NextToken()
		Token(Type='TokenType.INT', Literal='2')
		>>> l.NextToken()
		Token(Type='TokenType.RBRACKET', Literal=']')
		>>> l.NextToken()
		Token(Type='TokenType.SEMICOLON', Literal=';')
		>>> l.NextToken()
		Token(Type='TokenType.LBRACE', Literal='{')
		>>> l.NextToken()
		Token(Type='TokenType.STRING', Literal='foo')
		>>> l.NextToken()
		Token(Type='TokenType.COLON', Literal=':')
		>>> l.NextToken()
		Token(Type='TokenType.STRING', Literal='bar')
		>>> l.NextToken()
		Token(Type='TokenType.RBRACE', Literal='}')
		>>> l.NextToken()
		Token(Type='TokenType.EOF', Literal='')
		"""
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
