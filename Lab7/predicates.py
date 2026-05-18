def forall(pred, iterable):
    return all(map(pred, iterable))

def exists(pred, iterable):
    return any(map(pred, iterable))

def atleast(n, pred, iterable):
    return sum(map(pred, iterable)) >= n

def atmost(n, pred, iterable):
    return sum(map(pred, iterable)) <= n

def is_even(n):
    return n % 2 == 0

if __name__ == "__main__":
    a = [1, 2, 3, 4, 5]
    b = [2, 4, 6, 8]

    print(forall(is_even, iter(a)))
    print(forall(is_even, iter(b)))
    print(exists(is_even, iter(a)))
    print(exists(is_even, iter(b)))
    print(atleast(2, is_even, iter(a)))
    print(atleast(2, is_even, iter(b)))
    print(atmost(2, is_even, iter(a)))
    print(atmost(2, is_even, iter(b)))