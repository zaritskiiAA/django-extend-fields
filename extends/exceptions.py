import warnings
from colorama import Fore, Style


class ManagerBuilderExceptions(Exception):
    pass


def warning_message(msg: str):
    warnings.warn(Fore.YELLOW + msg + Style.RESET_ALL)
