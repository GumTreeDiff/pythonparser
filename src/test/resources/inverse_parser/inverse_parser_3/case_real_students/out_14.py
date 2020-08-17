a = int(input())
b = int(input())
c = int(input())
if a > b and a > c:
    print(a)
elif b > a and b > c:
    print(b)
elif c > a and c > b:
    print(c)
elif a == b:
    print(a, b)
elif a == c:
    print(a, c)
elif b == c:
    print(b, c)
elif a == b == c:
    print(a, b, c)
