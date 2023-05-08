import datetime
import decimal
import unittest.mock

import asyncio_zabbix_sender
import asyncio_zabbix_sender._response
import pytest

import router_log_preprocessor.domain
import router_log_preprocessor.util.rfc3164_parser

RECORD = router_log_preprocessor.domain.LogRecord(
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

MESSAGE = router_log_preprocessor.domain.WlcEventModel(
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


class MockedDatetime(datetime.datetime):
    faked_utcnow = None

    @classmethod
    def utcnow(cls):
        if cls.faked_utcnow is None:
            return super().utcnow()
        return cls.faked_utcnow



@pytest.fixture
def zabbix_sender():
    response = asyncio_zabbix_sender._response.ZabbixResponse(
        1, 0, 1, decimal.Decimal("0.001")
    )
    sender = unittest.mock.Mock(spec_set=asyncio_zabbix_sender.ZabbixSender)
    sender.send = unittest.mock.AsyncMock(return_value=response)
    return sender


@pytest.fixture(scope="function")
def zabbix_sender_exception(request):
    sender = unittest.mock.Mock(spec_set=asyncio_zabbix_sender.ZabbixSender)
    sender.send = RaiseOnce(request.param)
    return sender
