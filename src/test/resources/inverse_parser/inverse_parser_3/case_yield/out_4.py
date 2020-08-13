def coroutine():
    x = yield None
    yield 'You sent: %s' % x