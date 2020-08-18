class Power(object):

    def __init__(self, arg):
        self._arg = arg

    def __call__(self, a, b):
        return self._arg(a, b) ** 2


@Power
def mul(a, b):
    return a * b