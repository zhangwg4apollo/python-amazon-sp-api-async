from datetime import datetime, timedelta

import pytest
import pytz

from sp_api_async.api import Sales
from sp_api_async.base import Granularity

tz = pytz.timezone('US/Central')
fmt = '%Y-%m-%dT%H:%M:%S%z'

interval = (datetime.now(tz) - timedelta(days=185)), (datetime.now(tz))


@pytest.mark.asyncio
async def test_sales_granularity_total():
    async with Sales() as client:
        res = await client.get_order_metrics(interval, Granularity.TOTAL, granularityTimeZone='US/Central')
        assert res.payload[0].get('unitCount') == 2


@pytest.mark.asyncio
async def test_sales_granularity_day():
    async with Sales() as client:
        res = await client.get_order_metrics(interval, Granularity.DAY, granularityTimeZone='US/Central')
        assert res.payload[0].get('unitCount') == 1


@pytest.mark.asyncio
async def test_sales_granularity_total_by_asin():
    async with Sales() as client:
        res = await client.get_order_metrics(interval, Granularity.TOTAL, granularityTimeZone='US/Central', asin='B008OLKVEW')
        assert res.payload[0].get('unitCount') == 1


@pytest.mark.asyncio
async def test_sales_granularity_day_by_asin():
    async with Sales() as client:
        res = await client.get_order_metrics(interval, Granularity.DAY, granularityTimeZone='US/Central', asin='B008OLKVEW')
        assert res.payload[0].get('unitCount') == 1

