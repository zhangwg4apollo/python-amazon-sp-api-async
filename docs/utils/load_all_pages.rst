Load All Pages Decorator
========================

..  automethod:: sp_api_async.util.load_all_pages

The example below will load all pages, transforming the decorated function to an async generator.
The async generator yields a page at a time.

Some examples:

.. code-block:: python

    import asyncio
    from datetime import datetime, timedelta
    from sp_api_async.base import Marketplaces
    from sp_api_async.api import Orders
    from sp_api_async.util import throttle_retry, load_all_pages


    @throttle_retry()
    @load_all_pages()
    async def load_all_orders(**kwargs):
        """
        an async generator function to return all pages, obtained by NextToken
        """
        async with Orders() as client:
            return await client.get_orders(**kwargs)


    async def main():
        async for page in load_all_orders(LastUpdatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat()):
            for order in page.payload.get('Orders'):
                print(order)

    asyncio.run(main())


.. code-block:: python

    import asyncio
    from sp_api_async.api import Finances
    from sp_api_async.util import throttle_retry, load_all_pages

    @throttle_retry()
    @load_all_pages()
    async def get_financial_events(**kwargs):
        async with Finances() as client:
            return await client.list_financial_events(**kwargs)

    async def main():
        async for page in get_financial_events(PostedAfter='2021-05-10', PostedBefore='2021-05-11', MaxResultsPerPage=100):
            for event in page.payload.get('FinancialEvents').get('ShipmentEventList'):
                print(event)

    asyncio.run(main())


.. warning::

    Amazon's endpoints don't follow naming conventions within the API. The parameter `NextToken` sometimes is called `next_token`, or differently.
    @load_all_pages accepts `next_token_param` as a parameter:

    .. code-block:: python

        @load_all_pages(next_token_param='next_token')

    Now it will look for a key named `next_token` in payload, instead of `NextToken`

.. note::

    The decorator works with async functions and returns an async generator. Make sure to use ``async for`` when iterating over the results.


