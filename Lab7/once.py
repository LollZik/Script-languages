
def once(obj):
    has_run = False
    def decorator(*args, **kwargs):
        nonlocal has_run
        if not has_run:
            has_run = True
            return obj(*args, **kwargs)
    return decorator

@once
def multiply(a, b):
    return a * b

@once
def multiply1(a, b):
    return a * b

if __name__ == "__main__":
    wynik = multiply(4, 25)
    print(wynik)
    wynik1 = multiply(4, 25)
    print(wynik1)
    wynik2 = multiply(3, 4)
    print(wynik2)
    wynik3 = multiply1(3, 4)
    print(wynik3)
    wynik4 = multiply1(3, 4)
    print(wynik4)