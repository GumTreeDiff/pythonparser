s = input()
n = len(s)
ans = ''
if n % 2 == 0:
    for i in range(n // 2 - 1):
        ans += s[i] + '('
    ans += s[n // 2 - 1] + s[n // 2]
    for i in range(n // 2 + 1, n):
        ans += ')' + s[i]
    print(ans)
else:
    for i in range(n // 2):
        ans += s[i] + '('
    ans += s[n // 2]
    for i in range(n // 2 + 1, n):
        ans += ')' + s[i]
    print(ans)
