import pytest
from sp_api_async.api.external_fulfillment.external_fulfillment import ExternalFulfillment
from sp_api_async.base import SellingApiBadRequestException


@pytest.mark.asyncio
async def test_get_shipments():
    async with ExternalFulfillment() as client:
        res = await client.get_shipments(
        **{
            "locationId": "TEST_CASE_200_LOCATION_ID",
            "status": "CONFIRMED",
            "maxResults": 2,
        }
        )
        assert res.errors is None
        assert res.payload.get("shipments") is not None
        assert len(res.payload.get("shipments")) == 2


@pytest.mark.asyncio
async def test_get_shipments_error():
    async with ExternalFulfillment() as client:
        try:
            res = await client.get_shipments()
            assert res.errors is None
        except SellingApiBadRequestException as br:
            assert br.code == 400
            assert type(br) == SellingApiBadRequestException
            assert br.message == "Missing or invalid request parameters: [status]"
            assert br.amzn_code == "InvalidInput"


@pytest.mark.asyncio
async def test_get_shipment():
    async with ExternalFulfillment() as client:
        res = await client.get_shipment(
        "TEST_CASE_200_FBA_SHIPMENT_ID"
        )

        assert res.errors is None
        assert res.payload.get("locationId") == "ABCD"


@pytest.mark.asyncio
async def test_process_shipment_confirm():
    async with ExternalFulfillment() as client:
        res = await client.process_shipment(
        "TEST_CASE_200_FBA_SHIPMENT_ID",
        "CONFIRM"
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_process_shipment_out_stock():
    async with ExternalFulfillment() as client:
        res = await client.process_shipment(
        "TEST_CASE_200_FBA_SHIPMENT_ID",
        "REJECT",
        **{
            "referenceId": "cancellation-reference-identifier1",
            "lineItems": [
                {
                    "lineItem": {
                        "id": "1",
                        "quantity": 0
                    },
                    "reason": "OUT_OF_STOCK"
                }
            ]
        }
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_create_packages_fba():
    async with ExternalFulfillment() as client:
        res = await client.create_packages(
        "TEST_CASE_200_FBA_SHIPMENT_ID",
        **{
            "packages": []
        }
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_create_packages_mfn():
    async with ExternalFulfillment() as client:
        res = await client.create_packages(
        "TEST_CASE_200_MFN_SHIPMENT_ID",
        **{
            "packages": []
        }
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_update_package_fba():
    async with ExternalFulfillment() as client:
        res = await client.update_package(
        "TEST_CASE_200_FBA_SHIPMENT_ID",
        "TEST_CASE_200_PACKAGE_ID",
        **{
            "packages": []
        }
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_update_package_mfn():
    async with ExternalFulfillment() as client:
        res = await client.update_package(
        "TEST_CASE_200_MFN_SHIPMENT_ID",
        "TEST_CASE_200_PACKAGE_ID",
        **{
            "packages": []
        }
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_update_package_status():
    async with ExternalFulfillment() as client:
        res = await client.update_package_status(
        "TEST_CASE_200_MFN_SHIPMENT_ID",
        "TEST_CASE_200_PACKAGE_ID",
        **{
            "status": "SHIPPED"
        }
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_generate_invoice():
    async with ExternalFulfillment() as client:
        res = await client.generate_invoice(
        "TEST_CASE_200_FBA_SHIPMENT_ID"
    )

        assert res.errors is None
        assert res.payload.get("document").get("format") == "PDF"
        assert res.payload.get("document").get("content") is not None


@pytest.mark.asyncio
async def test_retrieve_invoice():
    async with ExternalFulfillment() as client:
        res = await client.retrieve_invoice(
        "TEST_CASE_200_FBA_SHIPMENT_ID"
    )

        assert res.errors is None
        assert res.payload.get("document").get("format") == "PDF"
        assert res.payload.get("document").get("content") is not None


@pytest.mark.asyncio
async def test_retrieve_shipping_options_mfn():
    async with ExternalFulfillment() as client:
        res = await client.retrieve_shipping_options(
        "TEST_CASE_200_MFN_SHIPMENT_ID",
        "TEST_CASE_200_PACKAGE_ID"
    )
    assert res.errors is None
    assert res.payload.get("shippingOptions") is not None
    assert len(res.payload.get("shippingOptions")) == 1
        assert res.payload.get("recommendedShippingOption") is not None


@pytest.mark.asyncio
async def test_retrieve_shipping_options_fba():
    async with ExternalFulfillment() as client:
        res = await client.retrieve_shipping_options(
        "TEST_CASE_200_FBA_SHIPMENT_ID",
        "TEST_CASE_200_PACKAGE_ID"
    )
        assert res.errors is None
        assert len(res.payload.get("shippingOptions")) == 0


@pytest.mark.asyncio
async def test_generate_ship_labels():
    async with ExternalFulfillment() as client:
        res = await client.generate_ship_labels(
        "TEST_CASE_200_FBA_SHIPMENT_ID",
        "GENERATE",
        **{
            "packageIds": [
                "TEST_CASE_200_PACKAGE_ID"
            ],
            "courierSupportedAttributes": {
                "carrierName": "ATS",
                "trackingId": "151958276037"
            }
        }
        )

        assert res.errors is None
        assert res.payload.get("packageShipLabelList") is not None
        assert len(res.payload.get("packageShipLabelList")) == 1


@pytest.mark.asyncio
async def test_generate_ship_labels_with_shipping_option():
    async with ExternalFulfillment() as client:
        res = await client.generate_ship_labels(
        "TEST_CASE_200_MFN_SHIPMENT_ID",
        "GENERATE",
        shippingOptionId="TEST_CASE_200_SHIPPING_OPTION_ID",
        **{
            "packageIds": [
                "TEST_CASE_200_PACKAGE_ID"
            ],
            "courierSupportedAttributes": {
                "carrierName": "ATSPL",
                "trackingId": "343284200328"
            }
        }
        )

        assert res.errors is None
        assert res.payload.get("packageShipLabelList") is not None
        assert len(res.payload.get("packageShipLabelList")) == 1


@pytest.mark.asyncio
async def test_retrieve_ship_label():
    async with ExternalFulfillment() as client:
        res = await client.retrieve_ship_label(
        "TEST_CASE_200_MFN_SHIPMENT_ID",
        "TEST_CASE_200_PACKAGE_ID"
    )

        assert res.errors is None
        assert res.payload.get("document") is not None
        assert res.payload.get("document").get("content") is not None


@pytest.mark.asyncio
async def test_list_returns():
    async with ExternalFulfillment() as client:
        res = await client.list_returns(
        **{
            "rmaId": "rmaIdOneShipmentOneItemOneQty200"
        }
        )

        assert res.errors is None
        assert len(res.payload.get("returns", [])) >= 0


@pytest.mark.asyncio
async def test_list_returns_by_return_location():
    async with ExternalFulfillment() as client:
        res = await client.list_returns(
        **{
            "returnLocationId": "testReturnLocationId",
            "status": "CREATED",
            "lastUpdatedAfter": "2021-03-20T00:00:00Z"
        }
        )

        assert res.errors is None
        assert len(res.payload.get("returns", [])) >= 0


@pytest.mark.asyncio
async def test_get_return():
    async with ExternalFulfillment() as client:
        res = await client.get_return(
        "rmaIdOneShipmentOneItemOneQty200"
    )

        assert res.errors is None
        assert res.payload.get("id") == "rmaIdOneShipmentOneItemOneQty200"


@pytest.mark.asyncio
async def test_process_return_item():
    async with ExternalFulfillment() as client:
        res = await client.process_return_item(
        "ee39cdd9-9caa-47b6-a5b1-7b6a1c6d43d1",
        **{
            "op": "increment",
            "path": "/processedReturns",
            "value": {
                "Sellable": 1
            }
        }
        )

        assert res.errors is None


@pytest.mark.asyncio
async def test_update_inventory():
    async with ExternalFulfillment() as client:
        res = await client.update_inventory(
    "43cd8cd4-a944-4fa8-a584-5e3b3efdb045",
    "efptestsku2",
    15
    )

        assert res.errors is None
        assert res.payload.get("sellableQuantity") == 15


@pytest.mark.asyncio
async def test_get_inventory():
    async with ExternalFulfillment() as client:
        res = await client.get_inventory(
    "43cd8cd4-a944-4fa8-a584-5e3b3efdb045",
    "efptestsku2"
    )

        assert res.errors is None
        assert res.payload.get("sellableQuantity") == 15


@pytest.mark.asyncio
async def test_batch_inventory():
    async with ExternalFulfillment() as client:
        res = await client.batch_inventory(
        ** {
            "requests": [
                {
                    "method": "POST",
                    "uri": "/inventory/update?locationId=EXSB&skuId=efptestsku1",
                    "body": {
                        "quantity": 15,
                        "clientSequenceNumber": 12345678,
                        "marketplaceAttributes": {
                            "marketplaceId": "AXJDDKDFDKDF",
                            "channelName": "FBA"
                        }
                    }
                },
                {
                    "method": "POST",
                    "uri": "/inventory/fetch?locationId=EXSB&skuId=efptestsku2",
                    "body": {
                        "marketplaceAttributes": {
                            "marketplaceId": "AXJDDKDFDKDF",
                            "channelName": "FBA"
                        }
                    }
                }
            ]
        }
        )

        assert res.errors is None
        assert len(res.payload.get("responses")) == 2
        assert res.payload.get("responses")[0].get("status").get("statusCode") == 200
        assert res.payload.get("responses")[1].get("status").get("statusCode") == 400