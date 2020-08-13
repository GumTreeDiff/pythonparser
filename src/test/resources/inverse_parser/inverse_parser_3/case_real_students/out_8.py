a = int(input())
b = int(input())
c = int(input())
max = 0
if a > b:
    max = a
else:
    max = b
if b > c:
    max = b
if c > max:
    max = c
print(max)
