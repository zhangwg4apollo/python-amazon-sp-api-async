import pytest
from sp_api_async.api import Inventories
from sp_api_async.base import SellingApiForbiddenException


@pytest.mark.asyncio
async def test_get_inventory_summary_marketplace():
    async with Inventories() as client:
        res = await client.get_inventory_summary_marketplace(**{
            "details": True,
            "marketplaceIds": ["ATVPDKIKX0DER"]
        })
        assert res.errors is None
        assert res.pagination.get('nextToken') == 'seed'
        assert res.payload.get('granularity').get('granularityType') == 'Marketplace'


@pytest.mark.asyncio
async def test_get_inventory_summary_marketplace_expect_500():
    async with Inventories() as client:
        try:
            await client.get_inventory_summary_marketplace(**{
                "marketplaceIds": ["1"],
            })
        except SellingApiForbiddenException as se:
            assert se.code == 403

