def coroutine():
    x = yield None
    yield 'You sent: %s' % x
def coroutine_wrapper():
    yield from coroutine()