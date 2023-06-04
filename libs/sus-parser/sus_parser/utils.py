from dataclasses import dataclass

BASE36_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def as_base36(i: int):
    l: list[int] = []
    while i > 0:
        l.append(i % 36)
        i = i // 36
    if not l:
        l.append(0)
    return "".join(BASE36_DIGITS[v] for v in reversed(l))
