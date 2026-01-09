import pytest
from sp_api_async.api import FbaInboundEligibility


@pytest.mark.asyncio
async def test_inbound_eligibility():
    async with FbaInboundEligibility() as client:
        res = await client.get_item_eligibility_preview(asin='TEST_CASE_200', program="INBOUND")
        assert res.payload is not None
