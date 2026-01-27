from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo
from pathlib import Path

from fake_useragent import UserAgent


def ask(question: str) -> bool:
    answer = input(f"{question} [Y/n]: ").lower().strip()

    if answer in {"y", "yes", ""}:
        return True
    return False


def get_user_agent() -> str:
    return UserAgent().random


def get_download_folder() -> Path:
    showinfo(
        "Директория для установки", 
        "Выберите директорию для установки",
    )
    return Path(askdirectory())
