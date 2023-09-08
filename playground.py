from lox.parser import Parser
from lox.scanner import Scanner

code = """
fun hello(a, b) {
    print "hello";
}
"""

tokens = Scanner(code).scan_tokens()
parser = Parser(tokens)
print(parser.parse())
