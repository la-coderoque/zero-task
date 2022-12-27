from random import choice

def random_word(length: int, symbols: str):
    chars = ''
    for _ in range(length):
        chars += choice(symbols)
    return chars
