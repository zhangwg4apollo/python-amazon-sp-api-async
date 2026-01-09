import pytest
from sp_api_async.api import FeedsV2 as Feeds
from sp_api_async.base import SellingApiBadRequestException, SellingApiServerException, SellingApiForbiddenException
from sp_api_async.base.feedTypes import FeedType


@pytest.mark.asyncio
async def test_create_feed():
    async with Feeds() as client:
        res = await client.create_feed(
            FeedType.POST_PRODUCT_DATA,
            '3d4e42b5-1d6e-44e8-a89c-2abfca0625bb',
             marketplaceIds=["ATVPDKIKX0DER", "A1F83G8C2ARO7P"]
        )
        assert res.payload.get('feedId') == '3485934'


@pytest.mark.asyncio
async def test_get_feed():
    feed_id = 'feedId1'
    async with Feeds() as client:
        res = await client.get_feed(feed_id)
        assert res.payload.get('feedId') == 'FeedId1'
        assert res.payload.get('processingStatus') == 'CANCELLED'


@pytest.mark.asyncio
async def test_get_feed_expect_400():
    async with Feeds() as client:
        try:
            await client.get_feed('badFeedId1')
        except SellingApiBadRequestException as br:
            assert type(br) == SellingApiBadRequestException
            assert br.code == 400


@pytest.mark.asyncio
async def test_get_feed_expect_500():
    async with Feeds() as client:
        try:
            await client.get_feed('giberish')
        except SellingApiServerException as br:
            assert type(br) == SellingApiServerException
            assert br.code == 500


@pytest.mark.asyncio
async def test_request():
    async with Feeds() as client:
        try:
            await client._request('', data={})
        except SellingApiForbiddenException:
            assert True


@pytest.mark.asyncio
async def test_get_feed_document():
    feed_document_id = '0356cf79-b8b0-4226-b4b9-0ee058ea5760'
    async with Feeds() as client:
        res = await client.get_feed_document(feed_document_id)
        assert 'TestSku102XmlParentã\x81\x8cã\x82\x93ã\x81°ã\x81£ã\x81¦' in res
