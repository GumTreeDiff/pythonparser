n = int(input())
a = []
s = 1
for i in range(n):
    a.append(int(input()))
for g in range(n):
    if a[g] == 0:
        s = 0
    if s == 0:
        print("YES")
    else:
        print("NO")
