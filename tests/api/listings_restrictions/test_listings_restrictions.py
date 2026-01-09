import pytest
from sp_api_async.api import ListingsRestrictions


@pytest.mark.asyncio
async def test_listing_restrictions():
    async with ListingsRestrictions() as client:
        res = await client.get_listings_restrictions(sellerId='A3F26DF64ZIPJZ', asin='B07HRD6JKK')
        assert res('restrictions') is not None
        assert isinstance(res('restrictions'), list)

