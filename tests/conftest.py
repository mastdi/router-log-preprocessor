import pytest

from tests.hooks.util import zabbix_sender, zabbix_sender_exception


@pytest.fixture
def anyio_backend():
    return "asyncio"
