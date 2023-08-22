#!/usr/bin/env python3
import argparse
from scanner import Scanner

hadError = False
# Hello World

def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    print(tokens)
    if hadError:
        sys.exit(65)


def error(line: int, message: str, where: str = ""):
    print(f"[line {line}] Error{where}: {message}")
    hadError = True

def run_file(filename: str) -> None:
    try:
        with open(filename, 'r') as file:
            run(file.read())
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


parser = argparse.ArgumentParser(description='lox interpreter')
parser.add_argument('filename', nargs='?')
def main():
    args = parser.parse_args()
    if args.filename is not None:
        run_file(args.filename)
    else:
        runPrompt()


if __name__ == "__main__":
    main()
