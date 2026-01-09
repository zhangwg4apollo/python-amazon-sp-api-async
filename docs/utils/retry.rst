Retry Decorators
================

..  automethod:: sp_api_async.util.retry
..  automethod:: sp_api_async.util.sp_retry
..  automethod:: sp_api_async.util.throttle_retry


The example below will retry the call when a throttled exception was thrown:

.. code-block:: python

    from sp_api_async.api import Orders
    from sp_api_async.util import throttle_retry

    @throttle_retry(tries=10, delay=5, rate=1.3)
    async def get_orders(**kwargs):
        async with Orders() as client:
            return await client.get_orders(**kwargs)


The example below will return all pages, retrying each call up to <times> times

.. code-block:: python

    from sp_api_async.api import Orders
    from sp_api_async.util import sp_retry, load_all_pages

    @sp_retry(tries=10, delay=10, rate=1.2)
    @load_all_pages()
    async def get_orders(**kwargs):
        async with Orders() as client:
            return await client.get_orders(**kwargs)
