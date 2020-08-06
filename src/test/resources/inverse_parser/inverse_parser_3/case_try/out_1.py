a = 3
b = 4
d = 0
try:
    a = a + 1
    c = b + 2
except ValueError as e:
    print(e)
    d += 2
except KeyError:
    print('test')
    d = 5
finally:
    print('test')
    a += 15