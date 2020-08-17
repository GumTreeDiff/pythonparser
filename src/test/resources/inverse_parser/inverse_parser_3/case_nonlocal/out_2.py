def foo():
    x = 'John'

    def foo_1():
        nonlocal x
        x = 'hello'
    foo_1()
    return x


print(foo())