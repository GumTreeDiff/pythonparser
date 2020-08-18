a = int(input())
b = int(input())
c = int(input())
if a > b and a > c:
    print(a)
if b > a and b > c:
    print(b)
if c > a and c > b:
    print(c)
if a > b and a == c or a > c and a == b:
    print(a)
if b > a and b == c or b > c and b == a:
    print(b)
if c > b and a == a or c > a and c == b:
    print(c)
