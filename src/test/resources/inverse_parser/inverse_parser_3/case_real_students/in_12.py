a = int(input())
b = int(input())
c = int(input())
if a > b and a > c:
    print(a)
elif b > a and b > c:
    print(b)
elif c > a and c > b:
    print(c)
elif b == a and a > c and b > c:
    print(a)
elif b == c and b > a and c > a:
    print(b)
elif a == c and a > b and c > b:
    print(a)
elif a == b == c:
    print(a)
