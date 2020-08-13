a = int(input())
b = int(input())
n = int(input())
r = a * n
c = b * n
while c >= 100:
    r += 1
    c -= 100
print(r, c)
