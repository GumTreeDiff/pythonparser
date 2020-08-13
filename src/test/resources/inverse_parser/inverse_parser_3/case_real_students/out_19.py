a = int(input())
b = int(input())
c = int(input())
z = []
o = []
if a == 1:
    o.append(a)
else:
    z.append(a)
if b == 1:
    o.append(b)
else:
    z.append(b)
if c == 1:
    o.append(c)
else:
    z.append(c)
l = len(z)
m = len(o)
if l < m:
    print(1)
elif l > m:
    print(0)
