a = int(input())
b = int(input())
n = int(input())
h = 0
rub = a * n
kop = b * n
if kop >= 100:
    h = kop // 100
    kop = kop % 100
    rub += h
print(rub, end= " ")
print(kop)