import pytest

from sp_api_async.api import Finances
from sp_api_async.base import SellingApiBadRequestException


@pytest.mark.asyncio
async def test_for_order():
    async with Finances() as client:
        res = await client.get_financial_events_for_order('485-734-5434857', MaxResultsPerPage=10)
        assert res.payload.get('NextToken') == 'Next token value'


@pytest.mark.asyncio
async def test_for_order_expect_400():
    async with Finances() as client:
        try:
            await client.get_financial_events_for_order('BAD-ORDER', MaxResultsPerPage=10)
        except SellingApiBadRequestException as br:
            assert br.code == 400
            assert type(br) == SellingApiBadRequestException

