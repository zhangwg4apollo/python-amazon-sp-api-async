import pytest
from sp_api_async.api import Notifications
from sp_api_async.base import NotificationType


@pytest.mark.asyncio
async def test_create_destination():
    async with Notifications() as client:
        res = await client.create_destination(name='test', arn='arn:aws:sqs:us-east-2:444455556666:queue1')
        assert res.payload.get("destinationId") == "TEST_CASE_200_DESTINATION_ID"
        assert res.payload.get("resource").get('sqs').get('arn') == "arn:aws:sqs:us-east-2:444455556666:queue1"


@pytest.mark.asyncio
async def test_create_subscription():
    async with Notifications() as client:
        res = await client.create_subscription(NotificationType.MFN_ORDER_STATUS_CHANGE, destination_id='dest_id')
        assert res.payload.get('destinationId') == 'TEST_CASE_200_DESTINATION_ID'
        assert res.payload.get('subscriptionId') == 'TEST_CASE_200_SUBSCRIPTION_ID'


@pytest.mark.asyncio
async def test_delete_subscription():
    async with Notifications() as client:
        res = await client.delete_notification_subscription(NotificationType.MFN_ORDER_STATUS_CHANGE, 'subscription_id')
        assert res.errors is None


@pytest.mark.asyncio
async def test_get_subscriptions():
    async with Notifications() as client:
        res = await client.get_subscription(NotificationType.REPORT_PROCESSING_FINISHED)
        assert res.payload.get('destinationId') == 'TEST_CASE_200_DESTINATION_ID'
        assert res.payload.get('subscriptionId') == 'TEST_CASE_200_SUBSCRIPTION_ID'
