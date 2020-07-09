#!/bin/python
"""
This module contains the abstract syntax tree node definitions.

>>> name = Identifier(Value="myVar", Token=tstoken.Token(Type=tstoken.TokenType.IDENT, Literal="myVar"))
>>> val = Identifier(Value="anotherVar", Token=tstoken.Token(Type=tstoken.TokenType.IDENT, Literal="anotherVar"))
>>> tok = tstoken.Token(Type=tstoken.TokenType.LET, Literal="let")
>>> stmts = [LetStatement(Token=tok, Name=name, Value=val)]
>>> p = Program(Statements=stmts)
>>> str(p)
'let myVar = anotherVar;'
"""

import typing

from . import tstoken

class Node():
	pass

class Expression(Node):
	def __init__(self, *args, Token: tstoken.Token = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Token = Token if Token else tstoken.Token()

	def expressionNode(self):
		return None

	def TokenLiteral(self) -> str:
		"""
		Outputs the literal token string of this expression.

		>>> Expression(Token=tstoken.Token(5, "5")).TokenLiteral()
		'5'
		"""
		if not isinstance(self.Token, tstoken.Token):
			raise TypeError(f"{self.Token} is not a Token, it's a {type(self.Token)}")
		return self.Token.Literal

class Identifier(Expression):
	def __init__(self, *args, Value: str = "", **kwargs):
		super().__init__(*args, **kwargs)
		self.Value = Value

	def __str__(self) -> str:
		return self.Value

class Statement(Node):
	def __init__(self, *args, Token: tstoken.Token = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Token = Token if Token else tstoken.Token()

	def statementNode(self):
		return None

	def TokenLiteral(self) -> str:
		return self.Token.Literal

class Program():
	def __init__(self, Statements: typing.List[Statement] = None):
		if Statements is None:
			self.Statements = []
		else:
			self.Statements = Statements


	def TokenLiteral(self) -> str:
		if self.Statements and len(self.Statements) > 0:
			return self.Statements[0].TokenLiteral()
		return ""

	def __str__(self) -> str:
		return "".join(str(s) for s in self.Statements)

#### STATEMENTS ####
class LetStatement(Statement):
	def __init__(self, *args, Name: Identifier = None, Value: Expression = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Name = Name if Name else Identifier()
		self.Value = Value

	def __str__(self):
		return f"{self.TokenLiteral()} {str(self.Name)} = {str(self.Value) if self.Value else ''};"

class ReturnStatement(Statement):
	def __init__(self, *args, ReturnValue: Expression = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.ReturnValue = ReturnValue if ReturnValue else Expression()

	def __str__(self) -> str:
		return f"{self.TokenLiteral()} {str(self.ReturnValue)};"

class ExpressionStatement(Statement):
	def __init__(self, *args, expression: Expression = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Expression = expression if expression else Expression()

	def __str__(self) -> str:
		return str(self.Expression) if self.Expression else ""

class BlockStatement(Statement):
	def __init__(self, *args, Statements: typing.List[Statement] = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Statements = Statements if Statements else []

	def __str__(self) -> str:
		return "".join(str(s) for s in self.Statements)

#### EXPRESSIONS ####
class Boolean(Expression):
	def __init__(self, *args, Value: str = "", **kwargs):
		super().__init__(*args, **kwargs)
		self.Value = Value

	def __str__(self) -> str:
		return self.Token.Literal

class IntegerLiteral(Expression):
	def __init__(self, *args, Value: int = 0, **kwargs):
		super().__init__(*args, **kwargs)
		self.Value = Value

	def __str__(self) -> str:
		return self.Token.Literal

class PrefixExpression(Expression):
	def __init__(self, *args, Operator: str = "", Right: Expression = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Operator = Operator
		self.Right = Right if Right else Expression()

	def __str__(self) -> str:
		return f"({self.Operator}{str(self.Right)})"

class InfixExpression(Expression):
	def __init__(self, *args, Left: Expression = None, Operator: str = "", Right: Expression = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Left = Left if Left else Expression()
		self.Operator = Operator
		self.Right = Right if Right else Expression()

	def __str__(self) -> str:
		return f"({str(self.Left)} {self.Operator} {str(self.Right)})"

class IfExpression(Expression):
	def __init__(self, *args, Condition: Expression = None, Consequence: BlockStatement = None, Alternative: BlockStatement = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Condition = Condition if Condition else Expression()
		self.Consequence = Consequence if Consequence else BlockStatement()
		self.Alternative = Alternative

	def __str__(self) -> str:
		ret = f"if{str(self.Condition)} {str(self.Consequence)}"
		if self.Alternative is not None:
			ret += f"else {str(self.Alternative)}"
		return ret

class FunctionLiteral(Expression):
	def __init__(self, *args, Parameters: typing.List[Identifier] = None, Body: BlockStatement = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Parameters = Parameters if Parameters else []
		self.Body = Body if Body else BlockStatement

	def __str__(self) -> str:
		return f"{self.TokenLiteral()}({', '.join(str(p) for p in self.Parameters)}) {str(self.Body)}"

class CallExpression(Expression):
	def __init__(self, *args, Function: Expression = None, Arguments: typing.List[Expression] = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Function = Function if Function else Expression()
		self.Arguments = Arguments if Arguments else []

	def __str__(self) -> str:
		return f"{str(self.Function)}({', '.join(str(a) for a in self.Arguments)})"

class StringLiteral(Expression):
	def __init__(self, *args, Value: str = "", **kwargs):
		super().__init__(*args, **kwargs)
		self.Value = Value

	def __str__(self) -> str:
		return self.Token.Literal

class ArrayLiteral(Expression):
	def __init__(self, *args, Elements: typing.List[Expression] = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Elements = Elements if Elements else []

	def __str__(self) -> str:
		return f"[{', '.join(str(e) for e in self.Elements)}]"

class IndexExpression(Expression):
	def __init__(self, *args, Left: Expression = None, Index: Expression = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Left = Left if Left else Expression()
		self.Index = Index if Index else Expression()

	def __str__(self) -> str:
		return f"({str(self.Left)}[{str(self.Index)}])"

class HashLiteral(Expression):
	def __init__(self, *args, Pairs: typing.Dict[Expression, Expression] = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.Pairs = Pairs if Pairs else {}

	def __str__(self) -> str:
		pstr = ', '.join(':'.join((k, v) for k,v in self.Pairs))
		return f"{{{pstr}}}"
