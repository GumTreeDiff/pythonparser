s = input()
if len(s) > 2:
    if len(s) % 2 == 0:
        s = '('.join(s[:int(len(s) / 2)]) + ')'.join(s[int(len(s) / 2):])
    else:
        s = '('.join(s[:int(len(s) / 2) + 1]) + ')' + ')'.join(s[int(len(s) /
            2 + 1):])
print(s)
