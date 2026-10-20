def test01():
    print('开始')
    return '你好'
    print('结束')


def test02():
    print('开始')
    yield '你好'
    print('结束')


if __name__ == '__main__':
    print('return测试:')
    print(test01())
    print('yield测试')
    for item in test02():
        print(item)