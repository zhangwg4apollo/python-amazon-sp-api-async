import pytest
from sp_api_async.api import Orders


@pytest.mark.asyncio
async def test_get_orders():
    async with Orders() as client:
        res = await client.get_orders(CreatedAfter='TEST_CASE_200', MarketplaceIds=["ATVPDKIKX0DER"])
        assert res.errors is None
        assert res.payload.get('Orders') is not None


@pytest.mark.asyncio
async def test_get_order_items():
    async with Orders() as client:
        res = await client.get_order_items('TEST_CASE_200')
        assert res.errors is None
        assert res.payload.get('AmazonOrderId') is not None


@pytest.mark.asyncio
async def test_get_order_address():
    async with Orders() as client:
        res = await client.get_order_address('TEST_CASE_200')
        assert res.errors is None
        assert res.payload.get('AmazonOrderId') is not None


@pytest.mark.asyncio
async def test_get_order_buyer_info():
    async with Orders() as client:
        res = await client.get_order_buyer_info('TEST_CASE_200')
        assert res.errors is None
        assert res.payload.get('AmazonOrderId') is not None


@pytest.mark.asyncio
async def test_get_order():
    async with Orders() as client:
        res = await client.get_order('TEST_CASE_200')
        assert res.errors is None
        assert res.payload.get('AmazonOrderId') is not None


@pytest.mark.asyncio
async def test_get_order_items_buyer_info():
    async with Orders() as client:
        res = await client.get_order_items_buyer_info('TEST_CASE_200')
        assert res.errors is None
        assert res.payload.get('AmazonOrderId') is not None


@pytest.mark.asyncio
async def test_get_orders_400_error():
    from sp_api_async.base import SellingApiBadRequestException
    async with Orders() as client:
        try:
            await client.get_orders(CreatedAfter='TEST_CASE_400')
        except SellingApiBadRequestException as sep:
            assert sep.code == 400
            assert sep.amzn_code == 'InvalidInput'


@pytest.mark.asyncio
async def test_get_order_api_response_call():
    async with Orders() as client:
        res = await client.get_order('TEST_CASE_200')
        print(res('DefaultShipFromLocationAddress'))
        assert res('DefaultShipFromLocationAddress') is not None
        assert res.errors is None
        assert res.payload.get('AmazonOrderId') is not None


@pytest.mark.asyncio
async def test_get_orders_attr():
    async with Orders() as client:
        res = await client.get_orders(CreatedAfter='TEST_CASE_200', MarketplaceIds=["ATVPDKIKX0DER"])
        assert res.Orders is not None
        assert res.errors is None
        assert res.payload.get('Orders') is not None


@pytest.mark.asyncio
async def test_get_order_api_response_call2():
    async with Orders() as client:
        res = await client.get_order('TEST_CASE_200')
        assert res() is not None
        assert isinstance(res(), dict)
        assert res.errors is None
        assert res.payload.get('AmazonOrderId') is not None


@pytest.mark.asyncio
async def test_update_shipment_status():
    async with Orders() as client:
        res = await client.update_shipment_status(
            order_id='123-1234567-1234567',
            marketplaceId='ATVPDKIKX0DER',
            shipmentStatus='ReadyForPickup'
        )
        assert res() is not None
        assert isinstance(res(), dict)
        assert res.errors is None
        assert res.payload.get("status_code") == 204


@pytest.mark.asyncio
async def test_confirm_shipment():
    async with Orders() as client:
        res = await client.confirm_shipment(
            order_id='123-1234567-1234567',
            marketplaceId='ATVPDKIKX0DER',
            packageDetail={
                'packageReferenceId': '0001',
                'carrierCode': 'DHL',
                "shippingMethod": 'Paket',
                'trackingNumber': '1234567890',
                'shipDate': '2023-03-19T12:00:00Z',
                'orderItems': [
                    {
                        'orderItemId': '123456789',
                        'quantity': 1
                    },
                    {
                        'orderItemId': '2345678901',
                        'quantity': 2
                    },
                ]
            }
        )
        assert res() is not None
        assert isinstance(res(), dict)
        assert res.errors is None
        assert res.payload.get("status_code") is None


@pytest.mark.asyncio
async def test_update_shipment_status_400_error():
    from sp_api_async.base import SellingApiBadRequestException
    async with Orders() as client:
        try:
            await client.update_shipment_status(
                order_id='123-1234567-1234567',
                marketplaceId='1',
                shipmentStatus='ReadyForPickup'
            )
        except SellingApiBadRequestException as sep:
            assert sep.code == 400
            assert sep.amzn_code == 'InvalidInput'
