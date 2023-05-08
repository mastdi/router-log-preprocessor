import unittest.mock

import asyncio_zabbix_sender
import pytest

import router_log_preprocessor.hooks.zabbix
import router_log_preprocessor.domain as domain
import router_log_preprocessor.util.rfc3164_parser


# All test functions in this module should be tested using anyio
pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


_RECORD = router_log_preprocessor.domain.LogRecord(
    facility=1,
    severity=5,
    timestamp=router_log_preprocessor.util.rfc3164_parser.timestamp_to_datetime(
        "Feb", "2", "13", "02", "51"
    ),
    hostname="GT-AX11000-ABCD-1234567-E",
    process="wlceventd",
    process_id=None,
    message="Not relevant for testing",
)

_MESSAGE = router_log_preprocessor.domain.WlcEventModel(
    location="wl0.1",
    mac_address=router_log_preprocessor.domain.MAC("AB:CD:EF:01:23:45"),
    status=0,
    event=router_log_preprocessor.domain.WlcEvent.DEAUTH_IND,
    rssi=0,
    reason="N/A",
)


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
    record = _RECORD
    message = _MESSAGE
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

        await zabbix_trapper.send(record, message)

    assert expected_raised.has_raised, "Should raise the exception once"
    assert expected_raised.call_count == 2, "Should only recurse once"

    logged_exception = next(
        record
        for record in caplog.records
        if record.message.startswith("Connection error to Zabbix server: ")
    )
    assert logged_exception.message.endswith(repr(expected_raised.exception))
