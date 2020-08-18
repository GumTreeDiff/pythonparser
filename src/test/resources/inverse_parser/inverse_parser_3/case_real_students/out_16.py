n = int(input())
A = [int(i) for i in input().split()]
k = 0
A = sorted(A)
while k > n and A[k] != 0 and A[k] < 1:
    k += 1
if A[k] == 0:
    print('YES')
else:
    print('NO')
