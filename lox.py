# TODO: add command line arguments to also run a file.
from scanner import Scanner

hadError = False


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    print(tokens)
    if hadError:
        sys.exit(65)


def error(line: int, message: str, where: str = ""):
    print(f"[line {line}] Error{where}: {message}")
    hadError = True


def runPrompt():
    while True:
        print("> ", end="")
        try:
            line = input()
        except EOFError:
            break
        run(line)


def main():
    runPrompt()


if __name__ == "__main__":
    main()
