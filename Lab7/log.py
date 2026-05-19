import logging
import time
from functools import wraps

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(level=logging.INFO):
    def decorator(obj):
        if isinstance(obj, type):
            og = obj.__init__
            @wraps(og)
            def class_wrapper(self, *args, **kwargs):
                logging.log(level,f"Instancjonowanie klasy: {obj.__name__} z argumentami: args={args}, kwargs={kwargs}")
                og(self, *args, **kwargs)

            obj.__init__ = class_wrapper
            return obj

        else:
            @wraps(obj)
            def function_wrapper(*args, **kwargs):
                czas_wywolania = time.strftime("%Y-%m-%d %H:%M:%S")
                start_time = time.perf_counter()

                result = obj(*args, **kwargs)

                end_time = time.perf_counter()
                duration = end_time - start_time

                msg = (
                    f"Funkcja: '{obj.__name__}' | "
                    f"Czas wywołania: {czas_wywolania} | "
                    f"Czas trwania: {duration:.6f}s | "
                    f"Argumenty: args={args}, kwargs={kwargs} | "
                    f"Zwrócono: {result}"
                )
                logging.log(level, msg)
                return result

            return function_wrapper

    return decorator


@log(level=logging.DEBUG)
def multiply(a, b):
    time.sleep(0.05)
    return a * b


@log(level=logging.WARNING)
class Produkt:
    def __init__(self, nazwa, cena):
        self.nazwa = nazwa
        self.cena = cena


if __name__ == "__main__":
    wynik = multiply(4, 25)

    print(f"Nazwa udekorowanej funkcji: {multiply.__name__}")
    print(f"Docstring funkcji:           {multiply.__doc__}")

    prod = Produkt("Laptop", 4500)
    print(f"Nazwa udekorowanej klasy:   {Produkt.__name__}")