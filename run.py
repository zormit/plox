#!/usr/bin/env python3
import argparse
import sys
from lox.error import error_handler
from lox.interpreter import Interpreter
from lox.resolver import Resolver
from lox.parser import Parser
from lox.scanner import Scanner

interpreter = Interpreter.with_time()


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()
    if error_handler.had_error:
        return

    resolver = Resolver(interpreter)
    resolver.resolve([s for s in statements if s is not None])
    if error_handler.had_error:
        return

    interpreter.interpret([s for s in statements if s is not None])


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
        error_handler.reset()


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
