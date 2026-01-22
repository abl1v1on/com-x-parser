def ask(question: str) -> bool:
    answer = input(f"{question} [Y/n]: ").lower().strip()

    if answer in {"y", "yes", ""}:
        return True
    return False
