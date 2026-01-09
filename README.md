[![CodeFactor](https://www.codefactor.io/repository/github/zhangwg4apollo/python-amazon-sp-api-async/badge)](https://www.codefactor.io/repository/github/zhangwg4apollo/python-amazon-sp-api-async)
[![Downloads](https://static.pepy.tech/badge/python-amazon-sp-api-async)](https://pepy.tech/project/python-amazon-sp-api-async)
[![Downloads](https://static.pepy.tech/badge/python-amazon-sp-api-async/month)](https://pepy.tech/project/python-amazon-sp-api-async)
[![Downloads](https://static.pepy.tech/badge/python-amazon-sp-api-async/week)](https://pepy.tech/project/python-amazon-sp-api-async)

# PYTHON-AMAZON-SP-API-ASYNC

## Amazon Selling-Partner API (Async Fork)

> **Note**: This is an async fork modified from [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api).

A wrapper to access **Amazon's Selling Partner API** with an easy-to-use async/await interface.

### ⚠️ Warning

> **⚠️ Important Notice**:
> 
> - This project has **not been rigorously tested** and is provided as-is. Use at your own risk.
> - If the original repository ([python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api)) implements async support in the future, this fork will become **obsolete** and should no longer be used.
> - Please monitor the original repository for official async support and migrate to it when available.

### 🙏 Acknowledgments

This project is based on [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api) with modifications. Special thanks to:

- **Original Author**: [@saleweaver](https://github.com/saleweaver) (Michael Primke)
- **Original Repository**: [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api)
- **Original Contributors**: Thanks to all developers who contributed to the original project

This fork version has been refactored for async/await support based on the original project, but the core architecture and API design philosophy are derived from the original project. If you find this project useful, please consider supporting the original project as well.

### 🔄 Key Changes

Main improvements in this fork compared to the original version:

- **✨ Full Async Support**: All API calls use `async/await` pattern, implemented with `httpx` for better concurrency performance
- **📦 Modern Build System**: Migrated to `pyproject.toml` and `uv` package manager for simplified dependency management
- **🐍 Python 3.13+**: Requires Python 3.13 or higher to leverage the latest language features
- **⚡ Performance Optimization**: Async I/O support, ideal for high-concurrency scenarios

### 📋 Differences from Original

| Feature | Original | This Fork |
|---------|----------|-----------|
| HTTP Client | `requests` (sync) | `httpx` (async) |
| API Call Pattern | Synchronous | `async/await` |
| Package Name | `python-amazon-sp-api` | `python-amazon-sp-api-async` |
| Python Version | >= 3.9 | >= 3.13 |
| Package Management | `setup.py` / `requirements.txt` | `pyproject.toml` / `uv` |

---

### SP-API fees & call optimization

With Amazon’s new SP-API pricing model (annual fees plus usage-based charges for GET requests), inefficient integrations will quickly become costly. If your systems rely on `python-amazon-sp-api` and you want to control these expenses, I offer consulting to review and optimize your implementation—such as replacing high-volume Orders API polling with report-based workflows and reducing unnecessary GET traffic wherever possible. If you’d like expert support preparing your SP-API usage for the upcoming pricing changes, feel free to get in touch.


<fees@clairinsights.com>

---

### 🚀 Version 2 🚀

Version 2 is currently being built - featuring pydantic, async support and better versioning. 
Check out v2-alpha here: [v2-alpha](https://github.com/saleweaver/python-amazon-sp-api/tree/v2-01)  

---

# 🌟 Thank you for using python-amazon-sp-api! 🌟

This tool helps developers and businesses connect seamlessly with Amazon's vast marketplace, enabling powerful automations and data management.

If you appreciate this project and find it useful, please consider supporting its continued development:

- 🙌 [GitHub Sponsors](https://github.com/sponsors/saleweaver)
- 🌐 BTC Address: `bc1q6uqgczasmnvnc5upumarugw2mksnwneg0f65ws`
- 🌐 ETH Address: `0xf59534F7a7F5410DBCD0c779Ac3bB6503bd32Ae5`

Your support helps keep the project alive and evolving, and is greatly appreciated!


----

### Documentation

Documentation is available [here](https://github.com/zhangwg4apollo/python-amazon-sp-api-async)


### Q & A

If you have questions, please ask them in GitHub discussions 

[![discussions](https://img.shields.io/badge/github-discussions-brightgreen?style=for-the-badge&logo=github)](https://github.com/zhangwg4apollo/python-amazon-sp-api-async/discussions)

or

[![join on slack](https://img.shields.io/badge/slack-join%20on%20slack-orange?style=for-the-badge&logo=slack)](https://join.slack.com/t/sellingpartnerapi/shared_invite/zt-zovn6tch-810j9dBPQtJsvw7lEXSuaQ)


### Installation

> **Note**: This fork version may not be published to PyPI yet. Please use the following installation methods:

```bash
# Using uv (recommended)
uv pip install python-amazon-sp-api-async

# Or using pip
pip install python-amazon-sp-api-async

# If you need AWS Secret Manager authentication support
pip install "python-amazon-sp-api-async[aws]"

# If you need AWS cached secrets support
pip install "python-amazon-sp-api-async[aws-caching]"

# Install from source
git clone https://github.com/zhangwg4apollo/python-amazon-sp-api-async.git
cd python-amazon-sp-api-async
uv pip install -e .
```

---
### Usage

```python
import asyncio
from sp_api_async.api import Orders
from sp_api_async.api import Reports
from sp_api_async.api import DataKiosk
from sp_api_async.api import Feeds
from sp_api_async.base import SellingApiException
from sp_api_async.base.reportTypes import ReportType
from datetime import datetime, timedelta

async def main():
    # DATA KIOSK API
    async with DataKiosk() as client:
        res = await client.create_query(query="{analytics_salesAndTraffic_2023_11_15{salesAndTrafficByAsin(startDate:\"2022-09-01\" endDate:\"2022-09-30\" aggregateBy:SKU marketplaceIds:[\"ATVPDKIKX0DER\"]){childAsin endDate marketplaceId parentAsin sales{orderedProductSales{amount currencyCode}totalOrderItems totalOrderItemsB2B}sku startDate traffic{browserPageViews browserPageViewsB2B browserPageViewsPercentage browserPageViewsPercentageB2B browserSessionPercentage unitSessionPercentageB2B unitSessionPercentage}}}}")
        print(res)

    # orders API
    async with Orders() as orders_client:
        try:
            res = await orders_client.get_orders(CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat())
            print(res.payload)  # json data
        except SellingApiException as ex:
            print(ex)

    # report request
    async with Reports() as reports_client:
        create_report_response = await reports_client.create_report(reportType=ReportType.GET_MERCHANT_LISTINGS_ALL_DATA)

    # submit feed
    # feeds can be submitted like explained in Amazon's docs, or simply by calling submit_feed
    async with Feeds() as feeds_client:
        await feeds_client.submit_feed(<feed_type>, <file_or_bytes_io>, content_type='text/tsv', **kwargs)

    # PII Data
    async with Orders(restricted_data_token='<token>') as orders_client:
        res = await orders_client.get_orders(CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat())

    # or use the shortcut
    async with Orders() as orders_client:
        orders = await orders_client.get_orders(
            LastUpdatedAfter=(datetime.utcnow() - timedelta(days=1)).isoformat()
        )

asyncio.run(main())
```

---


### New endpoints

You can create a new endpoint file by running `make_endpoint <model_json_url>`

```bash
make_endpoint https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/models/listings-restrictions-api-model/listingsRestrictions_2021-08-01.json
```

This creates a ready to use client. Please consider creating a pull request with the new code.


### ADVERTISING API

You can use nearly the same client for the Amazon Advertising API. [@denisneuf](https://github.com/denisneuf) has built [Python-Amazon-Advertising-API](https://github.com/denisneuf/python-amazon-ad-api) on top of this client.
Check it out [here](https://github.com/denisneuf/python-amazon-ad-api)

### DISCLAIMER

We are not affiliated with Amazon


### LICENSE

![License](https://img.shields.io/github/license/saleweaver/python-amazon-sp-api?style=for-the-badge)

This project follows the same MIT license as the original project.

---

### 📚 Related Links

- **This Repository**: [python-amazon-sp-api-async](https://github.com/zhangwg4apollo/python-amazon-sp-api-async)
- **Original Repository**: [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api)
- **Original Documentation**: [python-amazon-sp-api.readthedocs.io](https://python-amazon-sp-api.readthedocs.io/en/latest/)
- **Original PyPI Package**: [python-amazon-sp-api](https://pypi.org/project/python-amazon-sp-api/)

---

### Base Client

The client is pretty extensible and can be used for any other API. Check it out here:

[API Client](https://github.com/saleweaver/rapid_rest_client)


![Alt](https://repobeats.axiom.co/api/embed/25e8a3fe715fe68f2996ab99fe2e6188cd96a459.svg "Repobeats analytics image")
