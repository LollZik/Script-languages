from functools import reduce

def acronym(words):
    return ''.join(map(lambda w: w[0].upper(), words))

def median(values):
    s = sorted(values)
    n = len(s)
    return (s[(n - 1) // 2] + s[n // 2]) / 2

def pierwiastek(x, eps=0.01):
    step = lambda y: y - (y**2 - x) / (2 * y)
    iterate = lambda y: y if abs(y ** 2 - x) < eps else iterate(step(y))
    return iterate(x / 2)

def make_alpha_dict(str):
    words = str.split()
    chars = dict.fromkeys(c for c in str if c.isalpha())
    return {c: list(filter(lambda w: c in w, words)) for c in chars}

def flatten(lst):
    return reduce(lambda acc, x: acc + flatten(list(x)) if isinstance(x, (list, tuple)) else acc + [x],
        lst, [])

def group_anagrams(list):
        key = lambda w: ''.join(sorted(w))
        return reduce(lambda acc, w: {**acc, key(w): acc.get(key(w), []) + [w]}
                      ,list,{})


if __name__ == "__main__":
    print("a)")
    print(acronym(["Zakład", "Ubezpieczeń", "Społecznych"]))

    print("\nb)")
    print(median([1, 1, 19, 2, 3, 4, 4, 5, 1]))
    print(median([1, 2, 3, 4]))

    print("\nc)")
    print(pierwiastek(3.0, eps=0.1))
    print(pierwiastek(9.0, eps=0.1))

    print("\nd)")
    print(make_alpha_dict("on i ona"))

    print("\ne)")
    print(flatten([1, [2, 3], [[4, 5], 6]]))
    print(flatten([1, (2, [3, 4]), 5]))

    print("\nf)")
    print(group_anagrams(["kot", "tok", "pies", "kep", "pek"]))
