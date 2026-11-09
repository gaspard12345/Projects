import re

ISIN_PATTERN = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")


def is_valid_isin(code: str) -> bool:
    """Format check plus check digit (letters -> numbers, then Luhn)."""
    if not isinstance(code, str):
        return False
    code = code.strip().upper()
    if not ISIN_PATTERN.match(code):
        return False
    digits = "".join(str(int(ch, 36)) for ch in code[:-1])  # A=10 ... Z=35
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 0:          # double every second digit, starting from the right
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return (10 - total % 10) % 10 == int(code[-1])
