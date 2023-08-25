#!/usr/bin/env python3
import argparse
import sys
from lox.error import error_handler
from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.scanner import Scanner


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()
    if error_handler.had_error or expression is None:
        sys.exit(65)
    interpreter = Interpreter()
    interpreter.interpret(expression)


def run_file(filename: str) -> None:
    try:
        with open(filename, "r") as file:
            run(file.read())
        if error_handler.had_error:
            sys.exit(65)
        if error_handler.had_runtime_error:
            sys.exit(70)
    except FileNotFoundError as e:
        print(f"could not open {filename}: {e}")


def runPrompt():
    while True:
        print("> ", end="")
        try:
            line = input()
        except EOFError:
            break
        run(line)


parser = argparse.ArgumentParser(description="lox interpreter")
parser.add_argument("filename", nargs="?")


def main():
    args = parser.parse_args()
    if args.filename is not None:
        run_file(args.filename)
    else:
        runPrompt()


if __name__ == "__main__":
    main()
