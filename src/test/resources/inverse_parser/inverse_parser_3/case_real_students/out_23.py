x, y, z = map(int, input().split())
if x == y == 1:
    print(1)
elif x == z == 1:
    print(1)
elif z == y == 1:
    print(1)
elif z == x == y == 1:
    print(1)
else:
    print(0)
