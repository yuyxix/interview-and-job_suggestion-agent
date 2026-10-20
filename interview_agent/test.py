def test(k):
    b = []
    a = [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}, {'e': 5, 'f': 1}]
    for i in a:
        if k in i.values() or k in i.keys():
            b.append(i)
            print('k 在字典中')
        else:
            print('k 不在字典中')
    print(b)


if __name__ == '__main__':
    test(1)