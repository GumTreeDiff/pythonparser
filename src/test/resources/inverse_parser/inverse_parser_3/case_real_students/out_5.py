string = str(input())
max = '0'
for i in string:
    if i.isdigit():
        int(i)
        if i > max:
            max = i
print(max)
