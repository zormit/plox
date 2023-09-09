#!/usr/bin/env python3
from lox.parser import Parser
from lox.scanner import Scanner

code = """
class Breakfast {
  cook() {
    print "Eggs a-fryin'!";
  }

  serve(who) {
    print "Enjoy your breakfast, " + who + ".";
  }
}
var breakfast = Breakfast();
var person = "me";
breakfast.cook().serve(person);
"""

tokens = Scanner(code).scan_tokens()
parser = Parser(tokens)
statements = parser.parse()
breakpoint()
print("end")
