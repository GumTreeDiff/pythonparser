s = input()
length = len(s)
print(s[0], end='')
for i in range(1, length // 2 + length % 2):
    print('(' + s[i], end='')
if (length % 2 == 1):
    for i in range(length // 2 + length % 2, len(s)):
        print(')' + s[i], end='')
else:
    for i in range(length // 2, length - 1):
        print(s[i] + ')', end='')
    print(s[len(s) - 1])
