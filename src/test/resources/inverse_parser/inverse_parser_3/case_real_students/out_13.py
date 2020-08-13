x = int(input())
y = int(input())
z = int(input())
if x > y > z:
    print(x)
elif x > z > y:
    print(x)
elif y > z > x:
    print(y)
elif y > x > z:
    print(y)
elif z > y > x:
    print(z)
elif z > x > y:
    print(z)
