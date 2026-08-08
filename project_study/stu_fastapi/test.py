a = {'a': 3, 'b': 1, 'c': 2}
print(list(a.items()))
a = sorted(a.items(), key=lambda x: x[1])
print(a)

