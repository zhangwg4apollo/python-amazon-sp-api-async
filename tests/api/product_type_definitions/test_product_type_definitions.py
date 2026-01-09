import pytest
from sp_api_async.api import ProductTypeDefinitions


@pytest.mark.asyncio
async def test_get_product_type_definitions():
    async with ProductTypeDefinitions() as client:
        r = await client.get_definitions_product_type('LEGUME')
        assert r is not None
