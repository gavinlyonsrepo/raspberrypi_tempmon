"""
display.py
Console display helpers. coloured text,labels, lines and prompts
"""

# ANSI colour codes
_BLUE   = "\033[96m"
_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_RED    = "\033[91m"
_BOLD   = "\033[1m"
_END    = "\033[0m"


def line() -> None:
    """Print a horizontal separator line."""
    print(_BLUE + "=" * 80 + _END)


def green(text: str) -> None:
    """ Print Green text"""
    print(_GREEN + text + _END)


def red(text: str) -> None:
    """ Print Red text"""
    print(_RED + text + _END)


def blue(text: str) -> None:
    """ Print Blue text"""
    print(_BLUE + text + _END)


def yellow(text: str) -> None:
    """ Print Yellow text"""
    print(_YELLOW + text + _END)


def bold(text: str) -> None:
    """ Print Bold text"""
    print(_BOLD + text + _END)


def info(text: str) -> None:
    """ Print info label """
    yellow("  INFO : " + text)


def error(text: str) -> None:
    """ Print Error label """
    red("  ERROR : " + text)


def anykey(prompt: str = "") -> None:
    """ Print anykey prompt"""
    input("Press <Enter> to continue " + prompt)


def yesno(prompt: str = "Repeat?") -> bool:
    """Prompt user for yes/no. Returns True for 'y', False for 'n'."""
    while True:
        choice = input(f"{prompt} [y/n]: ").strip().lower()
        if choice == "y":
            return True
        if choice == "n":
            return False
        yellow("Please answer y or n.")
