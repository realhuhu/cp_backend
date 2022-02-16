import random


def numberCode(digit=4):
    code = ""
    for i in range(digit):
        code += str(random.randint(0, 9))
    return code


__all__ = [
    "numberCode",
]
