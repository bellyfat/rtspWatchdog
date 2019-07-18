from functools import partial
import rx
from rx import operators as ops

def high_order_subscribe(watchdog,observable,disposable):
    return watchdog.subscribe(observable)

def N(observer, disposable):
    observer.on_next("n")

watchdog = rx.subject.Subject()

buffer_signal = rx.create(partial(high_order_subscribe, watchdog))

buffer_signal.subscribe(
    on_next = lambda i: print(i),
    on_error = lambda e: None,
    on_completed = lambda: None,
)

repeater = rx.interval(5).pipe(
    ops.do_action(partial(N,watchdog))
)

repeater.subscribe(
    on_next = lambda i: print('repeater'),
    on_error = lambda e: None,
    on_completed = lambda: None,
)

while True:
    pass