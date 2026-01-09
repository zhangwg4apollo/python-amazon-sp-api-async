import pytest
from sp_api_async.api import Authorization


@pytest.mark.asyncio
async def test_get_auth_code():
    async with Authorization() as client:
        res = await client.get_authorization_code(mwsAuthToken='test', developerId='test', sellingPartnerId='test')
        assert res.payload['authorizationCode'] == 'ANDMxqpCmqWHJeyzdbMH'
