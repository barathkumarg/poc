import inspect

def func():
    num = 10
    string = 'abc'
    print(inspect.stack())
    return 'Done'

func()

