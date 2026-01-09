Versioning
==========


Some clients have multiple versions, and the versioning is done by setting the version when constructing a new client.

.. note::

    All clients have a default version, and if you don't specify a version, the default version will be used. The default version is the oldest version available at the time of the client's release.


To use the latest version available, you can use the `LATEST` enum.


.. code-block:: python

    from sp_api_async.api import CatalogItems, CatalogItemsVersion

    async with CatalogItems(version=CatalogItemsVersion.LATEST) as client:
        ...

