import functools

def make_generator(f):
    def generator():
        n = 1
        while True:
            yield f(n)
            n += 1

    return generator()

def make_generator_mem(f):
    @functools.cache
    def f_memoized(n):
        return f(n)

    return make_generator(f_memoized)

def fibonacci(n):
    if n <= 0:
        return 0
    if n == 1 or n == 2:
        return 1

    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

@functools.cache
def fibonaccirek(n):
    if n <= 0:
        return 0
    if n == 1 or n == 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

if __name__ == "__main__":
    print("Ciag fib")
    f = make_generator(fibonacci)
    print(next(f))
    print(next(f))
    print(next(f))
    print(next(f))
    print(next(f))

    print("Ciag arytmetyczny")
    ciag = lambda n: 10 * n + 2
    f1 = make_generator(ciag)
    print(next(f1))
    print(next(f1))
    print(next(f1))
    print(next(f1))

    print("Ciag fib z pamietaniem")
    f = make_generator_mem(fibonaccirek)
    print(next(f))
    print(next(f))
    print(next(f))
    print(next(f))
    print(next(f))

    print("Ciag arytmetyczny z pamietanem")
    f1 = make_generator_mem(ciag)
    print(next(f1))
    print(next(f1))
    print(next(f1))
    print(next(f1))