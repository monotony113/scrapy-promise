# MIT License
#
# Copyright (c) 2020 Tony Wu <tony[dot]wu(at)nyu[dot]edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Promise API for Scrapy."""

from notcallback import Promise
from scrapy.http import Request


def fetch(url, *, cls=Request, base: Request = None, callback=None, errback=None, **kwargs) -> Promise:
    """Return a Promise that resolves to a Scrapy Response.

    Parameters
    ----------
    url : str
        URL for the Request, forwarded to `scrapy.http.Request`
    cls : Type[Request], optional
        The Request class to use, by default `scrapy.http.Request`
    base : Request, optional
        An existing `Request` object. If supplied, use `base.replace()` to create the new request
        instead of creating one from scratch.
        by default None
    callback : Callable, optional
        The callback that will be used as the `on_fulfill` handler, by default None
    errback : Callable, optional
        The callback that will be used as the `on_reject` handler, by default None
        _`callback` and `errback` are provided for compatibility with existing calls to_
        _`scrapy.http.Request` only. You should use `Promise().then()` and `Promise().catch()`_
        _to add handlers._
    **kwargs :
        The remaining arguments are forwarded to the Request initializer.

    Returns
    -------
    Promise
        A Promise that will send the Request to Scrapy when yielded from or iterated over, whose `callback`
        and `errback` will be the `.then()` handlers of the Promise.

    Example
    -------
        def start_requests(self):
            return (
                fetch('https://httpbin.org/ip')
                .then(lambda response: fetch(json.loads(response.text)['origin']))
                .then(print)
                .catch(lambda exc: logging.getLogger().error(exc)))

    To attach a handler to the Promise, use `.then()`, to provide an error handler, use `.catch()`.
    Your response handler should accept only one positional argument, which is the `Response` object.
    Your error handler should accept only one positional argument, which is either a
    `twisted.python.failure.Failure` instance or an `Exception`.

    You can attach multiple handlers to the same Promise, which will be called in the order they are declared.
    You can also call `.then()` successively, since each `.then()` returns another Promise:

    >>> fetch(...).then(...).then(...).catch(...)

    Subsequent `.then()` handlers will receive the return value from the previous handler.

    If you return another `fetch()` Promise in your handler, that request will be scheduled, and the next handler
    will be called with the `Response` of this new request. This lets you schedule multiple requests in order.

    To schedule the request, `yield from` it. When the `Request` has been made, Scrapy will fulfill the
    Promise with the `Response` object, which will trigger all handlers you have registered for this Promise.

    If Scrapy encounters an exception while making the `Request` (such that it has to raise a
    `twisted.python.failure.Failure`), the exception will cause the Promise to reject, and error handlers
    (specified with `.catch()`) will be called, if any.

    Note that a Promise object is only ever evaluated once. To make another request, you make a new Promise
    using `fetch()`.

    You may also use other methods provided by the Promise API. In particular, aggregation methods such as
    `Promise.all()` may be useful:

        from notcallback import Promise

        def batch_request(self):
            yield from (
                Promise.all(
                    fetch('resource:1'),
                    fetch('resource:2'),
                    fetch('resource:3'))
                .then(process_responses)  # only called when all requests are done.
                .catch(...))

        def takes_first(self):
            yield from (
                Promise.race(
                    fetch('resource:us-west-1'),
                    fetch('resource:eu-central'),
                .then(process_responses)  # called as soon as one request is finished.
                .catch(...))

    See also
    --------
    `notcallback.Promise` : The full Promise API
    """
    def make_request(resolve, reject):
        if base:
            request = base.replace(url=url, callback=resolve, errback=reject, **kwargs)
        else:
            request = cls(url, callback=resolve, errback=reject, **kwargs)
        yield request

    promise = Promise(make_request)
    if callback and errback:
        promise = promise.then(callback, errback)
    elif callback:
        promise = promise.then(callback)
    elif errback:
        promise = promise.catch(errback)

    return promise
