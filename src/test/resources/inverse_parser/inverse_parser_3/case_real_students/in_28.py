s = input()
l = len(s)
s1 = s[:l // 2]
s2 = s[(l + 1) // 2:]
print('('.join(s1), end='')
if l % 2 == 1:
    ch = s[l // 2]
    if l > 1:
        ch = '(' + ch + ')'
    print(ch, sep='', end='')
print(')'.join(s2))
