import os
import pytest

from sp_api_async.base import AccessTokenClient
from sp_api_async.base import CredentialProvider
from sp_api_async.base import AuthorizationError
from sp_api_async.base.credential_provider import BaseCredentialProvider


refresh_token = '<refresh_token>'
lwa_app_id = '<lwa_app_id>'
lwa_client_secret = '<lwa_client_secret>'


@pytest.mark.asyncio
async def test_auth_exception():
    e = AuthorizationError(200, 'Foo', 999)
    assert e.status_code == 999
    assert e.error_code == 200
    assert e.message == 'Foo'


@pytest.mark.asyncio
async def test_credentials():
    os.environ['SP_API_REFRESH_TOKEN'] = refresh_token
    os.environ['LWA_APP_ID'] = lwa_app_id
    os.environ['LWA_CLIENT_SECRET'] = lwa_client_secret
    
    try:
        x = CredentialProvider()
        assert x.credentials is not None
        assert x.credentials.lwa_app_id is not None
        assert x.credentials.lwa_client_secret is not None
    finally:
        os.environ.pop('SP_API_REFRESH_TOKEN', None)
        os.environ.pop('LWA_APP_ID', None)
        os.environ.pop('LWA_CLIENT_SECRET', None)


@pytest.mark.asyncio
async def test_credentials_with_custom_provider():
    class CustomCredentialProvider(BaseCredentialProvider):
        def load_credentials(self):
            self.credentials = {
                "refresh_token": refresh_token,
                "lwa_app_id": lwa_app_id,
                "lwa_client_secret": lwa_client_secret,
            }

    cp = CredentialProvider(credential_providers=(CustomCredentialProvider,))
    assert cp.credentials is not None
    assert cp.credentials.refresh_token == "<refresh_token>"
    assert cp.credentials.lwa_app_id == "<lwa_app_id>"
    assert cp.credentials.lwa_client_secret == "<lwa_client_secret>"


@pytest.mark.asyncio
async def test_auth_client():
    client = AccessTokenClient(credentials=CredentialProvider(credentials=dict(
        refresh_token=refresh_token,
        lwa_app_id=lwa_app_id,
        lwa_client_secret=lwa_client_secret,
    )).credentials)
    x = client._auth_code_request_body('foo')
    assert x.get('grant_type') == 'authorization_code'

    try:
        await client.authorize_auth_code('foo')
    except AuthorizationError as e:
        assert isinstance(e, AuthorizationError)
    finally:
        await client.aclose()

    client2 = AccessTokenClient(credentials=CredentialProvider(credentials=dict(
        refresh_token=refresh_token,
        lwa_app_id=lwa_app_id,
        lwa_client_secret=lwa_client_secret,
    )).credentials)
    try:
        await client2._request('https://jsonplaceholder.typicode.com/posts/1', {}, {})
    except AuthorizationError as e:
        assert isinstance(e, AuthorizationError)
    finally:
        await client2.aclose()
