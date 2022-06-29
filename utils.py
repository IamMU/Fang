# Libraries
import sys

from colorama import Fore, Back, Style, init as colorama_init
import os

# Colorama stuff
colorama_init(autoreset=True)


# Functions
def log(category, msg):
    if category.lower() == "success":
        print(f"{Fore.GREEN}[ SUCCESS ] {msg}")
    elif category.lower() == "error":
        print(f"{Fore.RED}[ ERROR ] {msg}")
    elif category.lower() == "exception":
        print(f"{Fore.RED}[ EXCEPTION ] {msg} on line {sys.exc_info()[-1].tb_lineno}")
    elif category.lower() == "broadcast":
        print(f"{Fore.BLUE}[ BROADCAST ] {msg}")
    elif category.lower() == "info":
        print(f"{Fore.YELLOW}[ INFO ] {msg}")
    elif category.lower().startswith("send"):
        print(f"{Fore.MAGENTA}[ SENDING ] {msg}")
    elif category.lower().startswith("receiv"):
        print(f"{Fore.CYAN}[ RECEIVING ] {msg}")
    else:
        print(f"{Fore.WHITE}[ {category.upper()} ] {msg}")


def clear_screen():
    try:
        os.system("clear")
    except:
        os.system("cls")