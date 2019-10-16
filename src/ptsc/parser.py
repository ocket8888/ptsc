import enum
import typing

from . import ast
from . import lexer
from . import token

class Precedence(enum.IntEnum):
	LOWEST = 0
	EQUALS = 1
	LESSGREATER = 2
	SUM = 3
	PRODUCT = 4
	PREFIX = 5
	CALL = 6
	INDEX = 7

precedences: typing.Dict[token.TokenType, Precedence] = {
	token.TokenType.EQ: Precedence.EQUALS,
	token.TokenType.NOT_EQ: Precedence.EQUALS,
	token.TokenType.LT: Precedence.LESSGREATER,
	token.TokenType.GT: Precedence.LESSGREATER,
	token.TokenType.PLUS: Precedence.SUM,
	token.TokenType.MINUS: Precedence.SUM,
	token.TokenType.SLASH: Precedence.PRODUCT,
	token.TokenType.ASTERISK: Precedence.PRODUCT,
	token.TokenType.LPAREN: Precedence.CALL,
	token.TokenType.LBRACKET: Precedence.INDEX
}

class Parser():
	def __init__(self, l: lexer.Lexer):
		self.l = l
		self.errors: typing.List[str] = []

		self.curToken: token.Token = None
		self.peekToken: token.Token = None

		self.prefixParseFns = {
			token.TokenType.IDENT: self.parseIdentifier,
			token.TokenType.INT: self.parseIntegerLiteral,
			token.TokenType.STRING: self.parseStringLiteral,
			token.TokenType.BANG: self.parsePrefixExpression,
			token.TokenType.MINUS: self.parsePrefixExpression,
			token.TokenType.TRUE: self.parseBoolean,
			token.TokenType.FALSE: self.parseBoolean,
			token.TokenType.LPAREN: self.parseGroupedExpression,
			token.TokenType.IF: self.parseIfExpression,
			token.TokenType.FUNCTION: self.parseFunctionLiteral,
			token.TokenType.LBRACKET: self.parseArrayLiteral,
			token.TokenType.LBRACE: self.parseHashLiteral
		}

		self.infixParseFns = {
			token.TokenType.PLUS: self.parseInfixExpression,
			token.TokenType.MINUS: self.parseInfixExpression,
			token.TokenType.SLASH: self.parseInfixExpression,
			token.TokenType.ASTERISK: self.parseInfixExpression,
			token.TokenType.EQ: self.parseInfixExpression,
			token.TokenType.NOT_EQ: self.parseInfixExpression,
			token.TokenType.LT: self.parseInfixExpression,
			token.TokenType.GT: self.parseInfixExpression,
			token.TokenType.LPAREN: self.parseCallExpression,
			token.TokenType.LBRACKET: self.parseIndexExpression
		}

		self.nextToken()
		self.nextToken()

	def nextToken(self):
		self.curToken = self.peekToken
		self.peekToken = self.l.NextToken()

	def curTokenIs(self, t: token.TokenType) -> bool:
		return self.curToken.Type == t

	def peekTokenIs(self, t: token.TokenType) -> bool:
		return self.peekToken.Type == t

	def expectPeek(self, t: token.TokenType) -> bool:
		if self.peekTokenIs(t):
			self.nextToken()
			return True
		self.peekError(t)
		return False

	def Errors(self) -> typing.List[str]:
		return self.errors

	def peekError(self, t: token.TokenType):
		self.errors.append(f"expected next token to be {t}, got {self.peekToken.Type} instead")

	def noPrefixParseFnError(self, t: token.TokenType):
		self.errors.append(f"no prefix parse function for {t} found")

	def ParseProgram(self) -> ast.Program:
		p = ast.Program()

		while not self.curTokenIs(token.TokenType.EOF):
			stmt = self.parseStatement()
			if stmt is not None:
				p.Statements.append(stmt)
			self.nextToken()

		return p

	def parseStatement(self) -> ast.Statement:
		if self.curToken.Type == token.TokenType.LET:
			return self.parseLetStatement()
		if self.curToken.Type == token.TokenType.RETURN:
			return self.parseReturnStatement()
		return self.parseExpressionStatement()

	def parseLetStatement(self) -> ast.LetStatement:
		"""
		Parses a single assignment expression, e.g. 'let a = 5;'

		>>> p = Parser(lexer.Lexer("let x = 5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].TokenLiteral()
		'let'
		>>> p.Statements[0].Name.Value
		'x'
		>>> p.Statements[0].Name.TokenLiteral()
		'x'
		"""
		stmt = ast.LetStatement(Token=self.curToken)

		if not self.expectPeek(token.TokenType.IDENT):
			return None

		stmt.Name = ast.Identifier(Value=self.curToken.Literal, Token=self.curToken)

		if not self.expectPeek(token.TokenType.ASSIGN):
			return None

		self.nextToken()
		stmt.Value = self.parseExpression(Precedence.LOWEST)

		if self.peekTokenIs(token.TokenType.SEMICOLON):
			self.nextToken()

		return stmt

	def parseReturnStatement(self) -> ast.ReturnStatement:
		stmt = ast.ReturnStatement(Token=self.curToken)

		self.nextToken()

		stmt.ReturnValue = self.parseExpression(Precedence.LOWEST)

		if self.peekTokenIs(token.TokenType.SEMICOLON):
			self.nextToken()

		return stmt

	def parseExpressionStatement(self) -> ast.ExpressionStatement:
		stmt = ast.ExpressionStatement(Token=self.curToken)
		stmt.Expression = self.parseExpression(Precedence.LOWEST)

		if self.peekTokenIs(token.TokenType.SEMICOLON):
			self.nextToken()

		return stmt

	def parseExpression(self, prec: Precedence) -> typing.Optional[ast.Expression]:
		prefix = self.prefixParseFns.get(self.curToken.Type, None)
		if prefix is None:
			self.noPrefixParseFnError(self.curToken.Type)
			return None
		leftExp = prefix()

		while not self.peekTokenIs(token.TokenType.SEMICOLON) and prec < self.peekPrecedence():
			infix = self.infixParseFns.get(self.peekToken.Type, None)
			if infix is None:
				return leftExp

			self.nextToken()
			leftExp = infix(leftExp)

		return leftExp

	def peekPrecedence(self) -> Precedence:
		return precedences.get(self.peekToken.Type, Precedence.LOWEST)

	def curPrecedence(self) -> Precedence:
		return precedences.get(self.curToken.Type, Precedence.LOWEST)

	def parseIdentifier(self) -> ast.Expression:
		return ast.Identifier(Value=self.curToken.Literal, Token=self.curToken)

	def parseIntegerLiteral(self) -> typing.Optional[ast.Expression]:
		lit = ast.IntegerLiteral(Token=self.curToken.Literal)

		try:
			value = int(self.curToken.Literal)
		except (ValueError, TypeError):
			self.errors.append(f"could not parse {self.curToken} as integer")
			return None

		lit.Value = value
		return lit

	def parseStringLiteral(self) -> ast.Expression:
		return ast.StringLiteral(Value=self.curToken.Literal, Token=self.curToken)

	def parsePrefixExpression(self) -> ast.Expression:
		expr = ast.PrefixExpression(Operator=self.curToken.Literal, Token=self.curToken)

		self.nextToken()

		expr.Right = self.parseExpression()

		return expr

	def parseInfixExpression(self, left: ast.Expression) -> ast.Expression:
		expr = ast.InfixExpression(Left=left, Operator=self.curToken.Literal, Token=self.curToken)

		precedence = self.curPrecedence()
		self.nextToken()
		expr.Right = self.parseExpression(precedence)

		return expr

	def parseBoolean(self) -> ast.Expression:
		return ast.Boolean(Value=self.curTokenIs(token.TokenType.TRUE), Token=self.curToken)

	def parseGroupedExpression(self) -> typing.Optional[ast.Expression]:
		self.nextToken()
		exp = self.parseExpression(Precedence.LOWEST)

		return exp if self.expectPeek(token.TokenType.RPAREN) else None

	def parseIfExpression(self) -> typing.Optional[ast.Expression]:
		expr = ast.IfExpression(Token=self.curToken)

		if not self.expectPeek(token.TokenType.LPAREN):
			return None

		self.nextToken()
		expr.Condition = self.parseExpression(Precedence.LOWEST)

		if not self.expectPeek(token.TokenType.RPAREN):
			return None
		if not self.expectPeek(token.TokenType.LBRACE):
			return None

		expr.Consequence = self.parseBlockStatement()
		if self.peekTokenIs(token.TokenType.ELSE):
			self.nextToken()

			if not self.expectPeek(token.LBRACE):
				return None

			expr.Alternative = self.parseBlockStatement()

		return expr

	def parseBlockStatement(self) -> ast.BlockStatement:
		block = ast.BlockStatement(Token=self.curToken)

		self.nextToken()

		while not self.curTokenIs(token.TokenType.RBRACE) and not self.curTokenIs(token.TokenType.EOF):
			stmt = self.parseStatement()
			if stmt is not None:
				block.Statements.append(stmt)
			self.nextToken()

		return block

	def parseFunctionLiteral(self) -> typing.Optional[ast.Expression]:
		lit = ast.FunctionLiteral(Token=self.curToken)

		if not self.expectPeek(token.TokenType.LPAREN):
			return None

		lit.Parameters = self.parseFunctionParameters

		if not self.expectPeek(token.TokenType.LBRACE):
			return None

		lit.Body = self.parseBlockStatement()

		return lit

	def parseFunctionParameters(self) -> typing.List[ast.Identifier]:
		if self.peekTokenIs(token.TokenType.RPAREN):
			self.nextToken()
			return []

		self.nextToken()

		idents = [ast.Identifier(Value=self.curToken.Literal, Token=self.curToken)]

		while self.peekTokenIs(token.TokenType.COMMA):
			self.nextToken()
			self.nextToken()
			idents = [ast.Identifier(Value=self.curToken.Literal, Token=self.curToken)]

		if not self.expectPeek(token.TokenType.RPAREN):
			return None

		return idents

	def parseCallExpression(self, func: ast.Expression) -> ast.Expression:
		exp = ast.CallExpression(Function=func, Token=self.curToken)
		exp.Arguments = self.parseExpression(token.TokenType.RPAREN)
		return exp

	def parseExpressionList(self, end: token.TokenType) -> typing.Optional[typing.List[ast.Expression]]:
		if self.peekTokenIs(end):
			self.nextToken()
			return []

		self.nextToken()
		l = [self.parseExpression(Precedence.LOWEST)]

		while self.peekTokenIs(token.TokenType.COMMA):
			self.nextToken()
			self.nextToken()
			l.append(self.parseExpression(Precedence.LOWEST))

		return l if self.expectPeek(end) else None

	def parseArrayLiteral(self) -> ast.Expression:
		arr = ast.ArrayLiteral(Token=self.curToken)
		arr.Elements = self.parseExpressionList(token.TokenType.RBRACKET)
		return arr

	def parseIndexExpression(self, left: ast.Expression) -> typing.Optional[ast.Expression]:
		exp = ast.IndexExpression(Left=left, Token=self.curToken)

		self.nextToken()
		exp.Index = self.parseExpression(Precedence.LOWEST)

		return exp if self.expectPeek(token.TokenType.RBRACKET) else None

	def parseHashLiteral(self) -> typing.Optional[ast.Expression]:
		h = ast.HashLiteral(Token=self.curToken)

		while not self.peekTokenIs(token.TokenType.RBRACE):
			self.nextToken()
			key = self.parseExpression(Precedence.LOWEST)

			if not self.expectPeek(token.TokenType.COLON):
				return None

			self.nextToken()
			v = self.parseExpression(Precedence.LOWEST)

			h.Pairs[key] = v

			if not self.peekTokenIs(token.TokenType.RBRACE) and not self.expectPeek(token.TokenType.COMMA):
				return None

		return h if self.expectPeek(token.TokenType.RBRACE) else None

traceLevel = 0
traceIdentPlaceholder = '\t'

def identLevel() -> str:
	return "".join([traceIdentPlaceholder]*traceLevel)

def tracePrint(fs: str):
	print(identLevel, fs, sep="")

def trace(msg: str) -> str:
	traceLevel += 1
	tracePrint(f"BEGIN {msg}")
	return msg

def untrace(msg: str):
	tracePrint("END {msg}")
	traceLevel -= 1