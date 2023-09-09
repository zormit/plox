#!/usr/bin/env python3
from lox.parser import Parser
from lox.scanner import Scanner

code = """
var a = "global";
{
  fun showA() {
    print a; // this came from env_0
  }

  showA();
  var a = "block";
  showA();
}
"""

tokens = Scanner(code).scan_tokens()
parser = Parser(tokens)
statements = parser.parse()
breakpoint()
print("end")
