import unittest.mock

import asyncio_zabbix_sender
import pytest

import router_log_preprocessor.hooks.zabbix
import router_log_preprocessor.domain as domain
import router_log_preprocessor.util.rfc3164_parser
from tests.hooks.util import RECORD, MESSAGE

# All test functions in this module should be tested using anyio
pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


class RaiseOnce:
    def __init__(self, exception: Exception):
        self.exception = exception
        self.has_raised = False
        self.call_count = 0

    async def __call__(self, *args, **kwargs):
        self.call_count += 1
        if self.has_raised:
            return
        self.has_raised = True
        raise self.exception


@pytest.fixture(scope="function")
def zabbix_sender_exception(request):
    sender = unittest.mock.Mock(spec_set=asyncio_zabbix_sender.ZabbixSender)
    sender.send = RaiseOnce(request.param)
    return sender


@pytest.mark.parametrize(
    "zabbix_sender_exception",
    [
        ConnectionResetError("[Errno 104] Connection reset by peer"),
        ConnectionRefusedError("[Errno 111] Connect call failed ('example.org', 10051)")
    ],
    indirect=True
)
async def test_zabbix_hook_with_exception(
        zabbix_sender_exception,
        caplog: pytest.LogCaptureFixture
):
    expected_raised: RaiseOnce = zabbix_sender_exception.send

    with unittest.mock.patch.object(
        router_log_preprocessor.hooks.zabbix.ZabbixTrapper,
        "discover_client",
        return_value=0,
    ), unittest.mock.patch(
        "anyio.sleep"
    ):
        zabbix_trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(
            sender=zabbix_sender_exception, client_discovery_wait_time=30
        )

        await zabbix_trapper.send(RECORD, MESSAGE)

    assert expected_raised.has_raised, "Should raise the exception once"
    assert expected_raised.call_count == 2, "Should only recurse once"

    logged_exception = next(
        record
        for record in caplog.records
        if record.message.startswith("Connection error to Zabbix server: ")
    )
    assert logged_exception.message.endswith(repr(expected_raised.exception))
