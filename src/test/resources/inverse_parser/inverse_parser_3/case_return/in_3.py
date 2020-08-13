def foo(a):
    if a == 1:
        return a
    return foo(a - 1) + foo(a)