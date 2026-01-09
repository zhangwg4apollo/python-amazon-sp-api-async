import pytest
from sp_api_async.api import Catalog
from sp_api_async.base import SellingApiBadRequestException, ApiResponse


@pytest.mark.asyncio
async def test_get_catalog_item():
    async with Catalog() as client:
        res = await client.get_item('ASIN_200', MarketplaceId='TEST_CASE_200')
        assert res.errors is None
        assert isinstance(res, ApiResponse)


@pytest.mark.asyncio
async def test_list_catalog_items():
    async with Catalog() as client:
        res = await client.list_items(MarketplaceId='TEST_CASE_200', SellerSKU='SKU_200')
        assert res.errors is None


@pytest.mark.asyncio
async def test_list_catalog_expect_400():
    async with Catalog() as client:
        try:
            await client.list_items(MarketplaceId='TEST_CASE_400', SellerSKU='SKU_400')
        except SellingApiBadRequestException as br:
            assert type(br) == SellingApiBadRequestException

