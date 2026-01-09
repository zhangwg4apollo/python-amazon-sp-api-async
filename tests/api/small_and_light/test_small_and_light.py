import pytest
from sp_api_async.api import FbaSmallAndLight
from sp_api_async.base import Marketplaces


@pytest.mark.asyncio
async def test_get_small_and_light_eligibility_by_seller_sku():
    async with FbaSmallAndLight() as client:
        res = await client.get_small_and_light_eligibility_by_seller_sku('TEST_CASE_200')
        assert res.payload is not None


@pytest.mark.asyncio
async def test_get_small_and_light_fee_preview():
    async with FbaSmallAndLight() as client:
        res = await client.get_small_and_light_fee_preview(**{
            'marketplaceId': Marketplaces.US.marketplace_id,
            "items": [
                {
                    "asin": "B076ZL9PB5",
                    "price": {
                        "currencyCode": "USD",
                        "amount": 6.5
                    }
                }
            ]})
        assert res('data') is not None
        assert res.payload is not None


@pytest.mark.asyncio
async def test_delete_small_and_light_enrollment_by_seller_sku():
    async with FbaSmallAndLight() as client:
        res = await client.delete_small_and_light_enrollment_by_seller_sku('SKU_ENROLLED_FOR_SMALL_AND_LIGHT', marketplaceIds='ATVPDKIKX0DER')
        assert res('status_code') == 204


@pytest.mark.asyncio
async def test_get_small_and_light_enrollment_by_seller_sku():
    async with FbaSmallAndLight() as client:
        res = await client.get_small_and_light_enrollment_by_seller_sku('SKU_ENROLLED_IN_SMALL_AND_LIGHT')
        assert res('status') == 'ENROLLED'


@pytest.mark.asyncio
async def test_put_small_and_light_enrollment_by_seller_sku():
    async with FbaSmallAndLight() as client:
        res = await client.put_small_and_light_enrollment_by_seller_sku('SKU_ELIGIBLE_FOR_SMALL_AND_LIGHT')
        assert res() is not None
