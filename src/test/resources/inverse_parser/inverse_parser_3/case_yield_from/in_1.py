def writer_wrapper(coro):
    yield from coro