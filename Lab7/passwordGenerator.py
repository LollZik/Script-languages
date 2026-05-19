import random
import string

class PasswordGenerator:
    default = string.ascii_letters + string.digits
    def __init__(self, length, count, charset=default):
        self.length = length
        self.count = count
        self.charset = charset
        self.n = 0
    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.n >= self.count:
            raise StopIteration
        self.n += 1
        return ''.join(random.choices(self.charset, k=self.length))


if __name__ == "__main__":
    gen = PasswordGenerator(length=12, count=3)
    print(next(gen))
    print(next(gen))
    print(next(gen))

    try:
        print(next(gen))
    except StopIteration:
        print("StopIteration exception detected")

    print("\n\n")
    for pwd in PasswordGenerator(length=8, count=5, charset=string.digits):
        print(pwd)

    print("\n\n")
    for pwd in PasswordGenerator(length=6, count=4, charset=string.ascii_uppercase):
        print(pwd)




