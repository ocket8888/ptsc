import enum
import typing

from . import ast
from . import lexer
from . import tstoken

class Precedence(enum.IntEnum):
	LOWEST = 0
	EQUALS = 1
	LESSGREATER = 2
	SUM = 3
	PRODUCT = 4
	PREFIX = 5
	CALL = 6
	INDEX = 7

precedences: typing.Dict[tstoken.TokenType, Precedence] = {
	tstoken.TokenType.EQ: Precedence.EQUALS,
	tstoken.TokenType.NOT_EQ: Precedence.EQUALS,
	tstoken.TokenType.LT: Precedence.LESSGREATER,
	tstoken.TokenType.GT: Precedence.LESSGREATER,
	tstoken.TokenType.PLUS: Precedence.SUM,
	tstoken.TokenType.MINUS: Precedence.SUM,
	tstoken.TokenType.SLASH: Precedence.PRODUCT,
	tstoken.TokenType.ASTERISK: Precedence.PRODUCT,
	tstoken.TokenType.LPAREN: Precedence.CALL,
	tstoken.TokenType.LBRACKET: Precedence.INDEX
}

class Parser():
	"""
	Parser is the class responsible for parsing every part of a program. Pass it input through a
	lexer.Lexer object.

	>>> Parser(lexer.Lexer("-a*b;")).ParseProgram()
	((-a) * b)
	>>> Parser(lexer.Lexer("!-a;")).ParseProgram()
	(!(-a))
	>>> Parser(lexer.Lexer("a+b+c;")).ParseProgram()
	((a + b) + c)
	>>> Parser(lexer.Lexer("a+b-c;")).ParseProgram()
	((a + b) - c)
	>>> Parser(lexer.Lexer("a * b * c;")).ParseProgram()
	((a * b) * c)
	>>> Parser(lexer.Lexer("a * b / c;")).ParseProgram()
	((a * b) / c)
	>>> Parser(lexer.Lexer("a + b / c;")).ParseProgram()
	(a + (b / c))
	>>> Parser(lexer.Lexer("a + b * c + d / e - f;")).ParseProgram()
	(((a + (b * c)) + (d / e)) - f)
	>>> Parser(lexer.Lexer("3 + 4; -5 * 5;")).ParseProgram()
	(3 + 4)((-5) * 5)
	>>> Parser(lexer.Lexer("5 > 4 == 3 < 4;")).ParseProgram()
	((5 > 4) == (3 < 4))
	>>> Parser(lexer.Lexer("5 < 4 != 3 > 4;")).ParseProgram()
	((5 < 4) != (3 > 4))
	>>> Parser(lexer.Lexer("3 + 4 * 5 == 3 * 1 + 4 * 5;")).ParseProgram()
	((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))
	>>> Parser(lexer.Lexer("true;")).ParseProgram()
	true
	>>> Parser(lexer.Lexer("false;")).ParseProgram()
	false
	>>> Parser(lexer.Lexer("3 > 5 == false;")).ParseProgram()
	((3 > 5) == false)
	>>> Parser(lexer.Lexer("3 < 5 == true;")).ParseProgram()
	((3 < 5) == true)
	>>> Parser(lexer.Lexer("1 + (2 + 3) + 4;")).ParseProgram()
	((1 + (2 + 3)) + 4)
	>>> Parser(lexer.Lexer("(5 + 5) * 2;")).ParseProgram()
	((5 + 5) * 2)
	>>> Parser(lexer.Lexer("2 / (5 + 5);")).ParseProgram()
	(2 / (5 + 5))
	>>> Parser(lexer.Lexer("-(5 + 5);")).ParseProgram()
	(-(5 + 5))
	>>> Parser(lexer.Lexer("!(true == true);")).ParseProgram()
	(!(true == true))
	>>> Parser(lexer.Lexer("a + add(b * c) + d;")).ParseProgram()
	((a + add((b * c))) + d)
	>>> Parser(lexer.Lexer("add(a, b, 1, 2*3, 4+5, add(6, 7*8));")).ParseProgram()
	add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))
	>>> Parser(lexer.Lexer("add(a+b+c*d/f+g);")).ParseProgram()
	add((((a + b) + ((c * d) / f)) + g))
	>>> Parser(lexer.Lexer("a * [1, 2, 3, 4][b * c] * d;")).ParseProgram()
	((a * ([1, 2, 3, 4][(b * c)])) * d)
	>>> Parser(lexer.Lexer("add(a * b[2], b[1], 2 * [1, 2][1]);")).ParseProgram()
	add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))
	"""
	def __init__(self, l: lexer.Lexer):
		self.l = l
		self.errors: typing.List[str] = []

		self.curToken: tstoken.Token = None
		self.peekToken: tstoken.Token = None

		self.prefixParseFns = {
			tstoken.TokenType.IDENT: self.parseIdentifier,
			tstoken.TokenType.INT: self.parseIntegerLiteral,
			tstoken.TokenType.STRING: self.parseStringLiteral,
			tstoken.TokenType.BANG: self.parsePrefixExpression,
			tstoken.TokenType.MINUS: self.parsePrefixExpression,
			tstoken.TokenType.TRUE: self.parseBoolean,
			tstoken.TokenType.FALSE: self.parseBoolean,
			tstoken.TokenType.LPAREN: self.parseGroupedExpression,
			tstoken.TokenType.IF: self.parseIfExpression,
			tstoken.TokenType.FUNCTION: self.parseFunctionLiteral,
			tstoken.TokenType.LBRACKET: self.parseArrayLiteral,
			tstoken.TokenType.LBRACE: self.parseHashLiteral
		}

		self.infixParseFns = {
			tstoken.TokenType.PLUS: self.parseInfixExpression,
			tstoken.TokenType.MINUS: self.parseInfixExpression,
			tstoken.TokenType.SLASH: self.parseInfixExpression,
			tstoken.TokenType.ASTERISK: self.parseInfixExpression,
			tstoken.TokenType.EQ: self.parseInfixExpression,
			tstoken.TokenType.NOT_EQ: self.parseInfixExpression,
			tstoken.TokenType.LT: self.parseInfixExpression,
			tstoken.TokenType.GT: self.parseInfixExpression,
			tstoken.TokenType.LPAREN: self.parseCallExpression,
			tstoken.TokenType.LBRACKET: self.parseIndexExpression
		}

		self.nextToken()
		self.nextToken()

	def nextToken(self):
		self.curToken = self.peekToken
		self.peekToken = self.l.NextToken()

	def curTokenIs(self, t: tstoken.TokenType) -> bool:
		return self.curToken.Type == t

	def peekTokenIs(self, t: tstoken.TokenType) -> bool:
		return self.peekToken.Type == t

	def expectPeek(self, t: tstoken.TokenType) -> bool:
		if self.peekTokenIs(t):
			self.nextToken()
			return True
		self.peekError(t)
		return False

	def Errors(self) -> typing.List[str]:
		return self.errors

	def peekError(self, t: tstoken.TokenType):
		self.errors.append(f"expected next tstoken to be {t}, got {self.peekToken.Type} instead")

	def noPrefixParseFnError(self, t: tstoken.TokenType):
		self.errors.append(f"no prefix parse function for {t} found")

	def ParseProgram(self) -> ast.Program:
		p = ast.Program()

		while not self.curTokenIs(tstoken.TokenType.EOF):
			stmt = self.parseStatement()
			if stmt is not None:
				p.Statements.append(stmt)
			self.nextToken()

		return p

	def parseStatement(self) -> ast.Statement:
		if self.curToken.Type == tstoken.TokenType.LET:
			return self.parseLetStatement()
		if self.curToken.Type == tstoken.TokenType.RETURN:
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
		>>> p.Statements[0].Value.Value
		5
		>>> p = Parser(lexer.Lexer("let y = true;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].TokenLiteral()
		'let'
		>>> p.Statements[0].Name.Value
		'y'
		>>> p.Statements[0].Value.Value
		True
		>>> p = Parser(lexer.Lexer("let foobar = y;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].TokenLiteral()
		'let'
		>>> p.Statements[0].Name.Value
		'foobar'
		>>> p.Statements[0].Value.Value
		'y'
		"""
		stmt = ast.LetStatement(Token=self.curToken)

		if not self.expectPeek(tstoken.TokenType.IDENT):
			return None

		stmt.Name = ast.Identifier(Value=self.curToken.Literal, Token=self.curToken)

		if not self.expectPeek(tstoken.TokenType.ASSIGN):
			return None

		self.nextToken()
		stmt.Value = self.parseExpression(Precedence.LOWEST)

		if self.peekTokenIs(tstoken.TokenType.SEMICOLON):
			self.nextToken()

		return stmt

	def parseReturnStatement(self) -> ast.ReturnStatement:
		"""
		Parses the next return statement in the parser's lexer's input buffer.

		>>> p = Parser(lexer.Lexer("return true;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].TokenLiteral()
		'return'
		>>> p.Statements[0].ReturnValue.Value
		True
		>>> p.Statements[0].ReturnValue.TokenLiteral()
		'true'
		"""
		stmt = ast.ReturnStatement(Token=self.curToken)

		self.nextToken()

		stmt.ReturnValue = self.parseExpression(Precedence.LOWEST)

		if self.peekTokenIs(tstoken.TokenType.SEMICOLON):
			self.nextToken()

		return stmt

	def parseExpressionStatement(self) -> ast.ExpressionStatement:
		stmt = ast.ExpressionStatement(Token=self.curToken)
		stmt.Expression = self.parseExpression(Precedence.LOWEST)

		if self.peekTokenIs(tstoken.TokenType.SEMICOLON):
			self.nextToken()

		return stmt

	def parseExpression(self, prec: Precedence) -> typing.Optional[ast.Expression]:
		prefix = self.prefixParseFns.get(self.curToken.Type, None)
		if prefix is None:
			self.noPrefixParseFnError(self.curToken.Type)
			return None
		leftExp = prefix()

		while not self.peekTokenIs(tstoken.TokenType.SEMICOLON) and prec < self.peekPrecedence():
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
		"""
		Parses a single identifier expression, e.g. "a;"

		>>> p = Parser(lexer.Lexer("foobar;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Value
		'foobar'
		>>> p.Statements[0].Expression.TokenLiteral()
		'foobar'
		"""
		return ast.Identifier(Value=self.curToken.Literal, Token=self.curToken)

	def parseIntegerLiteral(self) -> typing.Optional[ast.Expression]:
		"""
		Parses a single literal integer expression, e.g. "5;"

		>>> p = Parser(lexer.Lexer("5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Value
		5
		>>> p.Statements[0].Expression.TokenLiteral()
		'5'
		"""
		lit = ast.IntegerLiteral(Token=self.curToken)

		try:
			value = int(self.curToken.Literal)
		except (ValueError, TypeError):
			self.errors.append(f"could not parse {self.curToken} as integer")
			return None

		lit.Value = value
		return lit

	def parseStringLiteral(self) -> ast.Expression:
		"""
		Parses a single string literal, e.g. 'hello world'.

		>>> p = Parser(lexer.Lexer('"hello world";')).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Value
		'hello world'
		"""
		return ast.StringLiteral(Value=self.curToken.Literal, Token=self.curToken)

	def parsePrefixExpression(self) -> ast.Expression:
		"""
		Parses an expression with a prefix operator, e.g. '!true;'

		>>> p = Parser(lexer.Lexer("!5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'!'
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("-15;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'-'
		>>> p.Statements[0].Expression.Right.Value
		15
		>>> p = Parser(lexer.Lexer("!true;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'!'
		>>> p.Statements[0].Expression.Right.Value
		True
		>>> p = Parser(lexer.Lexer("!false;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'!'
		>>> p.Statements[0].Expression.Right.Value
		False
		"""
		expr = ast.PrefixExpression(Operator=self.curToken.Literal, Token=self.curToken)

		self.nextToken()

		expr.Right = self.parseExpression(Precedence.PREFIX)

		return expr

	def parseInfixExpression(self, left: ast.Expression) -> ast.Expression:
		"""
		Parses a single infix-operator expression, e.g. "5+5;"

		>>> p = Parser(lexer.Lexer("5+5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'+'
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("5-5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'-'
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("5*5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'*'
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("5/5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'/'
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("5>5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'>'
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("5<5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'<'
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("5==5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'=='
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("5!=5;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'!='
		>>> p.Statements[0].Expression.Left.Value
		5
		>>> p.Statements[0].Expression.Right.Value
		5
		>>> p = Parser(lexer.Lexer("true==true;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'=='
		>>> p.Statements[0].Expression.Left.Value
		True
		>>> p.Statements[0].Expression.Right.Value
		True
		>>> p = Parser(lexer.Lexer("true!=false;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'!='
		>>> p.Statements[0].Expression.Left.Value
		True
		>>> p.Statements[0].Expression.Right.Value
		False
		>>> p = Parser(lexer.Lexer("false==false;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Operator
		'=='
		>>> p.Statements[0].Expression.Left.Value
		False
		>>> p.Statements[0].Expression.Right.Value
		False
		"""
		expr = ast.InfixExpression(Left=left, Operator=self.curToken.Literal, Token=self.curToken)

		precedence = self.curPrecedence()
		self.nextToken()
		expr.Right = self.parseExpression(precedence)

		return expr

	def parseBoolean(self) -> ast.Expression:
		"""
		Parses a single boolean-valued expression, e.g. "true".

		>>> p = Parser(lexer.Lexer("true;")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Value
		True
		>>> p.Statements[0].Expression.TokenLiteral()
		'true'
		"""
		return ast.Boolean(Value=self.curTokenIs(tstoken.TokenType.TRUE), Token=self.curToken)

	def parseGroupedExpression(self) -> typing.Optional[ast.Expression]:
		self.nextToken()
		exp = self.parseExpression(Precedence.LOWEST)

		return exp if self.expectPeek(tstoken.TokenType.RPAREN) else None

	def parseIfExpression(self) -> typing.Optional[ast.Expression]:
		"""
		Parses a single 'if' expression, e.g. "if (x < y) { x }"

		>>> p = Parser(lexer.Lexer("if (x<y) {x};")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Condition.Left.Value
		'x'
		>>> p.Statements[0].Expression.Condition.Operator
		'<'
		>>> p.Statements[0].Expression.Condition.Right.Value
		'y'
		>>> p.Statements[0].Expression.Alternative
		>>> body = p.Statements[0].Expression.Consequence.Statements
		>>> len(body)
		1
		>>> body[0].Expression.Value
		'x'
		>>>
		>>> p = Parser(lexer.Lexer("if(x<y){x;}else{y;};")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> exp = p.Statements[0].Expression
		>>> exp.Condition.Left.Value
		'x'
		>>> exp.Condition.Operator
		'<'
		>>> exp.Condition.Right.Value
		'y'
		>>> body = exp.Consequence.Statements
		>>> len(body)
		1
		>>> body[0].Expression.Value
		'x'
		>>> alt = exp.Alternative.Statements
		>>> len(alt)
		1
		>>> alt[0].Expression.Value
		'y'
		"""
		expr = ast.IfExpression(Token=self.curToken)

		if not self.expectPeek(tstoken.TokenType.LPAREN):
			return None

		self.nextToken()
		expr.Condition = self.parseExpression(Precedence.LOWEST)

		if not self.expectPeek(tstoken.TokenType.RPAREN):
			return None
		if not self.expectPeek(tstoken.TokenType.LBRACE):
			return None

		expr.Consequence = self.parseBlockStatement()
		if self.peekTokenIs(tstoken.TokenType.ELSE):
			self.nextToken()

			if not self.expectPeek(tstoken.TokenType.LBRACE):
				return None

			expr.Alternative = self.parseBlockStatement()

		return expr

	def parseBlockStatement(self) -> ast.BlockStatement:
		block = ast.BlockStatement(Token=self.curToken)

		self.nextToken()

		while not self.curTokenIs(tstoken.TokenType.RBRACE) and not self.curTokenIs(tstoken.TokenType.EOF):
			stmt = self.parseStatement()
			if stmt is not None:
				block.Statements.append(stmt)
			self.nextToken()

		return block

	def parseFunctionLiteral(self) -> typing.Optional[ast.Expression]:
		"""
		Parses a single literal function expression, e.g. "function(x,y) {x+y;}"

		>>> p = Parser(lexer.Lexer("function(x,y) {x+y}")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> len(p.Statements[0].Expression.Parameters)
		2
		>>> p.Statements[0].Expression.Parameters[0].Value
		'x'
		>>> p.Statements[0].Expression.Parameters[1].Value
		'y'
		>>> len(p.Statements[0].Expression.Body.Statements)
		1
		>>> p.Statements[0].Expression.Body.Statements[0].Expression.Operator
		'+'
		>>> p.Statements[0].Expression.Body.Statements[0].Expression.Left.Value
		'x'
		>>> p.Statements[0].Expression.Body.Statements[0].Expression.Right.Value
		'y'
		"""
		lit = ast.FunctionLiteral(Token=self.curToken)

		if not self.expectPeek(tstoken.TokenType.LPAREN):
			return None

		lit.Parameters = self.parseFunctionParameters()

		if not self.expectPeek(tstoken.TokenType.LBRACE):
			return None

		lit.Body = self.parseBlockStatement()

		return lit

	def parseFunctionParameters(self) -> typing.List[ast.Identifier]:
		"""
		Parses function parameter expressions.

		>>> p = Parser(lexer.Lexer("function() {}")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> len(p.Statements[0].Expression.Parameters)
		0
		>>> p.Statements[0].Expression.TokenLiteral()
		'function'
		>>> p = Parser(lexer.Lexer("function(x) {}")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> len(p.Statements[0].Expression.Parameters)
		1
		>>> p.Statements[0].Expression.TokenLiteral()
		'function'
		>>> p.Statements[0].Expression.Parameters[0].Value
		'x'
		>>> p = Parser(lexer.Lexer("function(x, y, z) {}")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> params = p.Statements[0].Expression.Parameters
		>>> len(params)
		3
		>>> p.Statements[0].Expression.TokenLiteral()
		'function'
		>>> params[0].Value
		'x'
		>>> params[1].Value
		'y'
		>>> params[2].Value
		'z'
		"""
		if self.peekTokenIs(tstoken.TokenType.RPAREN):
			self.nextToken()
			return []

		self.nextToken()

		idents = [ast.Identifier(Value=self.curToken.Literal, Token=self.curToken)]
		while self.peekTokenIs(tstoken.TokenType.COMMA):
			self.nextToken()
			self.nextToken()
			idents.append(ast.Identifier(Value=self.curToken.Literal, Token=self.curToken))

		if not self.expectPeek(tstoken.TokenType.RPAREN):
			return None

		return idents

	def parseCallExpression(self, func: ast.Expression) -> ast.Expression:
		"""
		Parses a single function call expression, e.g. "encodeURIComponent(x)"

		>>> p = Parser(lexer.Lexer("add(1, 2*3, 4+5);")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Function.Value
		'add'
		>>> args = p.Statements[0].Expression.Arguments
		>>> len(args)
		3
		>>> args[0].Value
		1
		>>> args[1].Left.Value
		2
		>>> args[1].Operator
		'*'
		>>> args[1].Right.Value
		3
		>>> args[2].Left.Value
		4
		>>> args[2].Operator
		'+'
		>>> args[2].Right.Value
		5
		"""
		exp = ast.CallExpression(Function=func, Token=self.curToken)
		exp.Arguments = self.parseExpressionList(tstoken.TokenType.RPAREN)
		return exp

	def parseExpressionList(self, end: tstoken.TokenType) -> typing.Optional[typing.List[ast.Expression]]:
		if self.peekTokenIs(end):
			self.nextToken()
			return []

		self.nextToken()
		l = [self.parseExpression(Precedence.LOWEST)]

		while self.peekTokenIs(tstoken.TokenType.COMMA):
			self.nextToken()
			self.nextToken()
			l.append(self.parseExpression(Precedence.LOWEST))

		return l if self.expectPeek(end) else None

	def parseArrayLiteral(self) -> ast.Expression:
		"""
		Parses a single array literal, e.g. '[1,2*2,3+3]'

		>>> p = Parser(lexer.Lexer("[1,2*2,3+3];")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> arr = p.Statements[0].Expression.Elements
		>>> len(arr)
		3
		>>> arr[0].Value
		1
		>>> arr[1].Left.Value
		2
		>>> arr[1].Operator
		'*'
		>>> arr[1].Right.Value
		2
		>>> arr[2].Left.Value
		3
		>>> arr[2].Operator
		'+'
		>>> arr[2].Right.Value
		3
		"""
		arr = ast.ArrayLiteral(Token=self.curToken)
		arr.Elements = self.parseExpressionList(tstoken.TokenType.RBRACKET)
		return arr

	def parseIndexExpression(self, left: ast.Expression) -> typing.Optional[ast.Expression]:
		"""
		Parses a single array index expression, e.g. 'arr[1+1]'.

		>>> p = Parser(lexer.Lexer("arr[1+1];")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> p.Statements[0].Expression.Left.Value
		'arr'
		>>> p.Statements[0].Expression.Left.TokenLiteral()
		'arr'
		>>> exp = p.Statements[0].Expression.Index
		>>> exp.Left.Value
		1
		>>> exp.Left.TokenLiteral()
		'1'
		>>> exp.Operator
		'+'
		>>> exp.Right.Value
		1
		>>> exp.Right.TokenLiteral()
		'1'
		"""
		exp = ast.IndexExpression(Left=left, Token=self.curToken)

		self.nextToken()
		exp.Index = self.parseExpression(Precedence.LOWEST)

		return exp if self.expectPeek(tstoken.TokenType.RBRACKET) else None

	def parseHashLiteral(self) -> typing.Optional[ast.Expression]:
		"""
		Parses a single object literal expression, e.g. '{"one":1, "two":2, "three": 3}'

		>>> p = Parser(lexer.Lexer('{"one": 1, "two": 2, "three": 3};')).ParseProgram()
		>>> len(p.Statements)
		1
		>>> pairs = p.Statements[0].Expression.Pairs
		>>> len(pairs)
		3
		>>> for k, v in pairs.items():
		... 	print(k.Value,v.Value)
		...
		one 1
		two 2
		three 3
		>>> p = Parser(lexer.Lexer("{}")).ParseProgram()
		>>> len(p.Statements)
		1
		>>> len(p.Statements[0].Expression.Pairs)
		0
		>>> p = Parser(lexer.Lexer('{"one": 0+1, "two": 10-8, "three": 15/5}')).ParseProgram()
		>>> len(p.Statements)
		1
		>>> pairs = p.Statements[0].Expression.Pairs
		>>> len(pairs)
		3
		>>> for k, v in pairs.items():
		... 	print(k.Value, v.Left.Value, v.Operator, v.Right.Value)
		...
		one 0 + 1
		two 10 - 8
		three 15 / 5
		"""
		h = ast.HashLiteral(Token=self.curToken)

		while not self.peekTokenIs(tstoken.TokenType.RBRACE):
			self.nextToken()
			key = self.parseExpression(Precedence.LOWEST)

			if not self.expectPeek(tstoken.TokenType.COLON):
				return None

			self.nextToken()
			v = self.parseExpression(Precedence.LOWEST)

			h.Pairs[key] = v

			if not self.peekTokenIs(tstoken.TokenType.RBRACE) and not self.expectPeek(tstoken.TokenType.COMMA):
				return None

		return h if self.expectPeek(tstoken.TokenType.RBRACE) else None

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
	tracePrint(f"END {msg}")
	traceLevel -= 1
