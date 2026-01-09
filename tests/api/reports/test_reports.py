import pytest
from sp_api_async.api import Reports
from sp_api_async.base import Marketplaces, Schedules, SellingApiBadRequestException, SellingApiServerException, \
    ProcessingStatus
from sp_api_async.base.reportTypes import ReportType


@pytest.mark.asyncio
async def test_create_report():
    async with Reports() as client:
        res = await client.create_report(
            reportType=ReportType.GET_MERCHANT_LISTINGS_ALL_DATA,
            dataStartTime='2019-12-10T20:11:24.000Z',
            marketplaceIds=[
                "A1PA6795UKMFR9",
                "ATVPDKIKX0DER"
            ])
        assert res.payload.get('reportId') == 'ID323'


@pytest.mark.asyncio
async def test_create_report_expect_400():
    async with Reports() as client:
        try:
            await client.create_report(
                reportType="BAD_FEE_DISCOUNTS_REPORT",
                dataStartTime="2019-12-10T20:11:24.000Z",
                marketplaceIds=[
                    "A1PA6795UKMFR9",
                    "ATVPDKIKX0DER"
                ])
        except SellingApiBadRequestException as br:
            assert br.code == 400


@pytest.mark.asyncio
async def test_create_report_expect_500():
    async with Reports() as client:
        try:
            await client.create_report(
                reportType="BAD_FEE_DISCasdafsdsfsdfsdOUNTS_REPORT",
                dataStartTime="2019-12-10T20:11:24.000Z",
                marketplaceIds=[
                    "A1PA6asfd795UKMFR9",
                    "ATVPDKIKX0DER"
                ])
        except SellingApiServerException as br:
            assert br.code == 500


@pytest.mark.asyncio
async def test_get_report():
    async with Reports() as client:
        res = await client.get_report('ID323')
        assert res.payload.get('reportId') == 'ReportId1'
        assert res.payload.get('reportType') == 'FEE_DISCOUNTS_REPORT'


@pytest.mark.asyncio
async def test_get_report_document_n_decrypt():
    async with Reports() as client:
        res = await client.get_report_document('0356cf79-b8b0-4226-b4b9-0ee058ea5760', decrypt=False)
        assert res.errors is None
        assert 'document' not in res.payload


@pytest.mark.asyncio
async def test_create_report_schedule():
    async with Reports() as client:
        res = await client.create_report_schedule(reportType='FEE_DISCOUNTS_REPORT',
                                                   period=Schedules.MINUTES_5.value,
                                                   nextReportCreationTime="2019-12-10T20:11:24.000Z",
                                                   marketplaceIds=["A1PA6795UKMFR9", "ATVPDKIKX0DER"])
        assert res.errors is None
        assert 'reportScheduleId' in res.payload


@pytest.mark.asyncio
async def test_delete_schedule_by_id():
    async with Reports() as client:
        res = await client.delete_report_schedule('ID')
        assert res.errors is None


@pytest.mark.asyncio
async def test_get_schedule_by_id():
    async with Reports() as client:
        res = await client.get_report_schedule('ID323')
        assert res.errors is None
        assert 'period' in res.payload
        assert res.payload.get('reportType') == 'FEE_DISCOUNTS_REPORT'


@pytest.mark.asyncio
async def test_get_reports_1():
    report_types = [
        "FEE_DISCOUNTS_REPORT",
        "GET_AFN_INVENTORY_DATA"
    ]
    processing_status = [
        "IN_QUEUE",
        "IN_PROGRESS"
    ]
    async with Reports() as client:
        res = await client.get_reports(reportTypes=report_types, processingStatuses=processing_status)
        assert res.errors is None


@pytest.mark.asyncio
async def test_get_reports_2():
    report_types = [
        "FEE_DISCOUNTS_REPORT",
        "GET_AFN_INVENTORY_DATA"
    ]
    processing_status = [
        ProcessingStatus.IN_QUEUE,
        ProcessingStatus.IN_PROGRESS
    ]
    async with Reports() as client:
        res = await client.get_reports(reportTypes=report_types, processingStatuses=processing_status)
        assert res.errors is None


@pytest.mark.asyncio
async def test_get_reports_3():
    report_types = [
        ReportType.FEE_DISCOUNTS_REPORT,
        ReportType.GET_AFN_INVENTORY_DATA
    ]
    processing_status = [
        ProcessingStatus.IN_QUEUE,
        ProcessingStatus.IN_PROGRESS
    ]
    async with Reports() as client:
        res = await client.get_reports(reportTypes=report_types, processingStatuses=processing_status)
        assert res.errors is None


@pytest.mark.asyncio
async def test_get_reports_4():
    report_types = [
        ReportType.FEE_DISCOUNTS_REPORT,
        ReportType.GET_AFN_INVENTORY_DATA
    ]
    processing_status = [
        ProcessingStatus.IN_QUEUE,
        ProcessingStatus.IN_PROGRESS
    ]
    async with Reports() as client:
        res = await client.get_reports(reportTypes=report_types, processingStatuses=processing_status,
                                       marketplaceIds=[Marketplaces.US, Marketplaces.US.marketplace_id])
        assert res.errors is None
