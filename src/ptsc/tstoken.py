import enum

class TokenType(enum.Enum):
	ILLEGAL = "ILLEGAL"
	EOF = "EOF"

	IDENT = "IDENT"
	INT = "INT"
	STRING = "STRING"

	ASSIGN = "="
	PLUS = "+"
	MINUS = "-"
	BANG = "!"
	ASTERISK = "*"
	SLASH = "/"

	LT = "<"
	GT = ">"

	EQ = "=="
	NOT_EQ = "!="

	COMMA = ","
	SEMICOLON = ";"
	COLON = ":"

	LPAREN = "("
	RPAREN = ")"
	LBRACE = "{"
	RBRACE = "}"
	LBRACKET = "["
	RBRACKET = "]"

	FUNCTION = "FUNCTION"
	LET = "LET"
	TRUE = "TRUE"
	FALSE = "FALSE"
	IF = "IF"
	ELSE = "ELSE"
	RETURN = "RETURN"

class Token:
	def __init__(self, Type: TokenType = TokenType.ILLEGAL, Literal: str = ""):
		self.Type = Type
		self.Literal = Literal

keywords = {
	"function": TokenType.FUNCTION,
	"let": TokenType.LET,
	"true": TokenType.TRUE,
	"false": TokenType.FALSE,
	"if": TokenType.IF,
	"else": TokenType.ELSE,
	"return": TokenType.RETURN
}

def lookupIdent(ident: str) -> TokenType:
	return keywords.get(ident, TokenType.IDENT)