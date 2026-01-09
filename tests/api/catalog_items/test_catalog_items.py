import pytest
from sp_api_async.api import CatalogItems as Catalog, CatalogItemsVersion
from sp_api_async.base import ApiResponse


@pytest.mark.asyncio
async def test_get_catalog_item():
    async with Catalog(version=CatalogItemsVersion.V_2020_12_01) as client:
        res = await client.get_catalog_item('B098RX87V2')
        assert res.errors is None
        assert isinstance(res, ApiResponse)

        # No `includedData` parameter provided - Amazon should default to
        # "summaries".
        assert 'summaries' in res.payload


@pytest.mark.asyncio
async def test_get_catalog_item_version():
    async with Catalog(version=CatalogItemsVersion.LATEST) as client:
        res = await client.get_catalog_item('B098RX87V2')
        assert res.errors is None
        assert isinstance(res, ApiResponse)


@pytest.mark.asyncio
async def test_list_catalog_items():
    async with Catalog() as client:
        res = await client.search_catalog_items(keywords='test')
        assert res.errors is None

        # No `includedData` parameter provided - Amazon should default to
        # "summaries" for every returned item.
        for item in res.items:
            assert 'summaries' in item


@pytest.mark.asyncio
async def test_get_catalog_item_foo():
    async with Catalog(version=CatalogItemsVersion.V_2020_12_01) as client:
        res = await client.get_catalog_item('B07Z95MG3S')
        assert res.errors is None
        assert isinstance(res, ApiResponse)
