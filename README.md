# scrapy-promise

Promise API for making Scrapy requests.

## Usage & Examples

```python
from scrapy_promise import fetch
```

The `Promise` here works like Promise in JavaScript. If you are new to Promise, a great starting point would be MDN's
[Promise API reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
and the guide to [Using Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises).

### Creating and making requests

`fetch()` accepts all arguments that `scrapy.http.Request` accepts, except for `callback` and `errback`

```python
>>> fetch('https://example.org/login', method='POST', meta={'username': 'admin'})
```

`fetch()` returns a `Promise` object, which is an iterator/generator. You can return it directly in `start_requests`,
or `yield from` it in an existing callback.

### Adding handlers

If you only call `fetch()` and yield from it, then all it does is storing the response once the request is finished:

```python
request = fetch('https://httpbin.org/ip')
yield from request
# When the request is done
>>> request.is_fulfilled
True
>>> request.get()
<200 https://httpbin.org/ip>
```

`fetch()` returns a `Promise` object. Call its `.then()` method and provide a callable, and `Promise` will call it once there is a response.

`.then()` returns another `Promise` that you can `yield from`:

```python
def on_fulfill(response: TextResponse):
    # You can yield items from your handler
    # just like you would in a Scrapy callback
    yield Item(response)

>>> yield from fetch(...).then(on_fulfill)
```

You can also attach an error handler with `.catch()`, which will receive either a Twisted
[`Failure`](https://twistedmatrix.com/documents/current/api/twisted.python.failure.Failure.html) or an Exception:

```python
def on_reject(exc: Union[Failure, Exception]):
    if isinstance(exc, Failure):
        exc = exc.value
    ...

>>> yield from fetch(...).then(on_fulfill).catch(on_reject)
# will catch both exceptions during the request
# and exceptions raised in on_fulfill
```

### Branching and chaining

Because `.then()` and `.catch()` return another Promise, you can chain additional handlers.

Subsequent handlers
will receive the **return** value of the previous handler. _This is different from an ordinary Scrapy callback,_
where returning a value has no effect:

```python
yield from (
    fetch('https://httpbin.org/ip')
    .then(parse_json)   # returns dict
    .then(create_item)  # will be passed the dict from the previous handler
    .catch(lambda exc: logging.getLogger().error(exc)))
```

**Dynamic chaining**: If you return another `fetch()` request in your handler, that request will be scheduled,
and the next handler will be called with the `Response` of this new request. This lets you schedule multiple
requests in order. 

```python
yield from (
    fetch('https://httpbin.org/ip')
    # A second Request is created from the response of the first one and is scheduled.
    .then(lambda response: fetch(json.loads(response.text)['origin']))
    .then(lambda response: (yield Item(response)))
    .catch(lambda exc: logging.getLogger().error(exc)))
```

Note that only the request you _returned_ will be connected to subsequent handlers, `Request`s that are yielded
in the middle of the handler will be scheduled directly by Scrapy.

You can also attach multiple handlers to one request, and they will be evaluated in the order they were
declared:

```python
resource = fetch(...)
resource.then(save_token)
resource.then(parse_html).catch(log_error)
resource.then(next_page).catch(stop_spider)
yield from resource  # Evaluating any Promise in a chain/branch causes
                     # the entire Promise tree to be evaluated.
```

### Promise aggregation functions

`Promise` provides several aggregation functions that let you better control the how the requests are scheduled.

```python
from notcallback import Promise  # dependency
```

**`Promise.all()`** will only fulfill when all requests are made successfully, and will reject as soon as one of
the requests failed. If all the requests succeed, the handler will receive a list of Responses:

```python
def parse_pages(responses: Tuple[TextResponse]):
    for r in responses:
        ...

yield from Promise.all(*[fetch(url) for url in urls]).then(parse_pages)
```

**`Promise.race()`** will fulfill as soon as one of the requests is fulfilled/rejected.

```python
def select_fastest_cdn():
    yield from (
        Promise.race(*[fetch(url, method='HEAD') for url in cdn_list])
        .then(crawl_server))
```

**`Promise.all_settled()`** always fulfills when all requests are finished, regardless of whether or not
they are successful. The handler will receive a list of `Promise`s whose value (the response) can be accessed
with the `.get()` method:

```python
def report(promises: Tuple[Promise]):
    for promise in promises:
        result = promise.get()
        if isinstance(result, Response):
            log.info(f'Crawled {result.url}')
        else:
            log.warn(f'Encountered error {result}')

yield from Promise.all_settled(*[fetch(u) for u in urls]).then(report)
```

**`Promise.any()`** fulfills with the first request that fulfills, and rejects if no request is successful:

```python
def download(response):
    ...

yield from (
    Promise.any(*[fetch(u) for u in urls])
    .then(download)
    .catch(lambda exc: log.warn('No valid URL!')))
```

For more info on the `Promise API`, see [notcallback](https://github.com/monotony113/notcallback)

## See also

Other ways to schedule requests within a callback:
- [`twisted.internet.defer.inlineCallbacks(f)`](https://twistedmatrix.com/documents/current/api/twisted.internet.defer.inlineCallbacks.html)
- [scrapy-inline-requests](https://github.com/rmax/scrapy-inline-requests)
