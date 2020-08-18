N = int(input())
s = 0
for i in range(N):
    a = int(input())
    if a == 0:
        s += 1
if s == 0:
    print('NO')
else:
    print('YES')
