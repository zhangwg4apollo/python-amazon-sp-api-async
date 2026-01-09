import pytest
from sp_api_async.api import ListingsItems
from sp_api_async.base import Marketplaces


@pytest.mark.asyncio
async def test_get_listings_item():
    async with ListingsItems() as client:
        res = await client.get_listings_item('xxx', 'xxx')
        assert res is not None

@pytest.mark.asyncio
async def test_search_listings_items():
    async with ListingsItems() as client:
        res = await client.search_listings_items('xxx')
        assert res is not None


@pytest.mark.asyncio
async def test_put_listings_item():
    async with ListingsItems() as client:
        res = await client.put_listings_item('xxx', 'xxx', body={
                  "productType": "string",
                  "requirements": "LISTING",
                  "attributes": {},

                }, marketplaceIds=[Marketplaces.US.marketplace_id])
        assert res('status') == 'ACCEPTED'


@pytest.mark.asyncio
async def test_patch_listings_item():
    async with ListingsItems() as client:
        res = await client.patch_listings_item('xxx', 'xxx', body={
                  "productType": "string",
                  "patches": [
                    {
                      "op": "add",
                      "path": "string",
                      "value": [
                        {}
                      ]
                    }
                  ]
                })
        assert res('status') == 'ACCEPTED'


@pytest.mark.asyncio
async def test_delete_listings_item():
    async with ListingsItems() as client:
        res = await client.delete_listings_item('xxx', 'xxx')
        assert res('status') == 'ACCEPTED'
