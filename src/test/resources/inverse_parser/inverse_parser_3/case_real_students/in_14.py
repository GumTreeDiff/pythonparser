a = int(input())
b = int(input())
c = int(input())
if a > b and a > c:
    print(a)
else:
    if b > a and b > c:
        print(b)
    else:
        if c > a and c > b:
            print(c)
        else:
            if a == b:
                print(a, b)
            else:
                if a == c:
                    print(a, c)
                else:
                    if b == c:
                        print(b, c)
                    else:
                        if a == b == c:
                            print(a, b, c)
