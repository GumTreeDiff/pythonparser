def writer_wrapper(coro):
    coro.send(None)
    while True:
        try:
            x = (yield)
            coro.send(x)
        except StopIteration:
            pass