my_list = [int(input('enter 0 or 1: ')) for _ in range(3)]
print('1' if sum(my_list) > 1 else '0')