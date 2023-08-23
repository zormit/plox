import pytest

from lox.scanner import Scanner

def test_dot():
    scanner = Scanner("1.2+3a.5")
    assert str(scanner.scan_tokens()) == "[Token(token_type=<TokenType.NUMBER: 22>, lexeme='1.2', literal=1.2, line=1), Token(token_type=<TokenType.PLUS: 8>, lexeme='+', literal=None, line=1), Token(token_type=<TokenType.NUMBER: 22>, lexeme='3', literal=3.0, line=1), Token(token_type=<TokenType.IDENTIFIER: 20>, lexeme='a', literal=None, line=1), Token(token_type=<TokenType.DOT: 6>, lexeme='.', literal=None, line=1), Token(token_type=<TokenType.NUMBER: 22>, lexeme='5', literal=5.0, line=1), Token(token_type=<TokenType.EOF: 39>, lexeme='', literal=None, line=1)]"

def test_all():
    scanner = Scanner(
"""andy formless fo _ _123 _abc ab123
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_
and class else false for fun if nil or return super this true var while
123
123.456
.456
123.
(){};,+-*!===<=>=!=<>/.
""
"string"

space    tabs				newlines



end

""")
    filename = "tests/scanner_golden/out.tokens"
    # with open(filename,"w") as out:
    #     out.write("\n".join(map(str, scanner.scan_tokens())))
    with open(filename,"r") as expected:
        for token in scanner.scan_tokens():
            expected_token = expected.readline().strip()
            assert str(token) ==  expected_token
