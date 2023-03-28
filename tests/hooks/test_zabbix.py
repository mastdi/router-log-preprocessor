#  Copyright (c) 2023. Martin Storgaard Dieu <martin@storgaarddieu.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import datetime
import unittest.mock

import pytest
import pyzabbix

import asus_router_logger.domain
import asus_router_logger.hooks.zabbix
import asus_router_logger.util.rfc3164_parser


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def zabbix_sender():
    response = pyzabbix.ZabbixResponse()
    response._processed = 1
    sender = unittest.mock.MagicMock()
    sender.send = unittest.mock.MagicMock(return_value=response)
    return sender


# All test functions in this module should be tested using anyio
pytestmark = pytest.mark.anyio

_RECORD = asus_router_logger.domain.LogRecord(
    facility=1,
    severity=5,
    timestamp=asus_router_logger.util.rfc3164_parser.timestamp_to_datetime(
        "Feb", "2", "13", "02", "51"
    ),
    hostname="GT-AX11000-ABCD-1234567-E",
    process="wlceventd",
    process_id=None,
    message="Not relevant for testing",
)

_MESSAGE = asus_router_logger.domain.WlcEventModel(
    location="wl0.1",
    mac_address=asus_router_logger.domain.MAC("AB:CD:EF:01:23:45"),
    status=0,
    event=asus_router_logger.domain.WlcEvent.DEAUTH_IND,
    rssi=0,
    reason="N/A",
)


class MockedDatetime(datetime.datetime):
    faked_utcnow = None

    @classmethod
    def utcnow(cls):
        if cls.faked_utcnow is None:
            return super().utcnow()
        return cls.faked_utcnow


async def test_discover_client_not_known(zabbix_sender):
    zabbix_trapper = asus_router_logger.hooks.zabbix.ZabbixTrapper(
        sender=zabbix_sender, client_discovery_wait_time=30
    )

    wait_time = await zabbix_trapper.discover_client(_RECORD, _MESSAGE)

    assert wait_time == 30
    zabbix_sender.send.assert_called_once()


async def test_discover_client_just_known(zabbix_sender):
    zabbix_trapper = asus_router_logger.hooks.zabbix.ZabbixTrapper(
        sender=zabbix_sender, client_discovery_wait_time=30
    )
    original_datetime = datetime.datetime
    first_call_time = datetime.datetime.utcnow()
    next_call_time = first_call_time + datetime.timedelta(seconds=15)
    try:
        datetime.datetime = MockedDatetime
        MockedDatetime.faked_utcnow = first_call_time
        await zabbix_trapper.discover_client(_RECORD, _MESSAGE)
        zabbix_sender.send.reset_mock()

        MockedDatetime.faked_utcnow = next_call_time
        wait_time = await zabbix_trapper.discover_client(_RECORD, _MESSAGE)
    finally:
        datetime.datetime = original_datetime
        MockedDatetime.faked_utcnow = None
    assert wait_time == 15
    zabbix_sender.send.assert_not_called()


async def test_discover_client_known_and_discovered(zabbix_sender):
    zabbix_trapper = asus_router_logger.hooks.zabbix.ZabbixTrapper(
        sender=zabbix_sender, client_discovery_wait_time=30
    )
    original_datetime = datetime.datetime
    first_call_time = datetime.datetime.utcnow()
    next_call_time = first_call_time + datetime.timedelta(seconds=42)
    try:
        datetime.datetime = MockedDatetime
        MockedDatetime.faked_utcnow = first_call_time
        await zabbix_trapper.discover_client(_RECORD, _MESSAGE)
        zabbix_sender.send.reset_mock()

        MockedDatetime.faked_utcnow = next_call_time
        wait_time = await zabbix_trapper.discover_client(_RECORD, _MESSAGE)
    finally:
        datetime.datetime = original_datetime
        MockedDatetime.faked_utcnow = None
    assert wait_time == 0
    zabbix_sender.send.assert_not_called()


async def test_send_new_client(zabbix_sender):
    total_wait_time = 42
    with unittest.mock.patch.object(
        asus_router_logger.hooks.zabbix.ZabbixTrapper,
        "discover_client",
        return_value=total_wait_time,
    ) as mocked_discover_client:
        trapper = asus_router_logger.hooks.zabbix.ZabbixTrapper(
            zabbix_sender, total_wait_time
        )

        with unittest.mock.patch("anyio.sleep") as mocked_sleep:
            await trapper.send(_RECORD, _MESSAGE)

    mocked_discover_client.assert_called()
    # Ensure that the send method adheres to the wait time
    mocked_sleep.assert_called_once_with(total_wait_time)
    zabbix_sender.send.assert_called_once()


async def test_send_known_client(zabbix_sender):
    with unittest.mock.patch.object(
        asus_router_logger.hooks.zabbix.ZabbixTrapper, "discover_client", return_value=0
    ) as mocked_discover_client:
        trapper = asus_router_logger.hooks.zabbix.ZabbixTrapper(zabbix_sender, 42)

        with unittest.mock.patch("anyio.sleep") as mocked_sleep:
            await trapper.send(_RECORD, _MESSAGE)

    mocked_discover_client.assert_called()
    mocked_sleep.assert_not_called()
    zabbix_sender.send.assert_called_once()


async def test_send_message_none(zabbix_sender):
    with unittest.mock.patch.object(
        asus_router_logger.hooks.zabbix.ZabbixTrapper, "discover_client", return_value=0
    ) as mocked_discover_client:
        zabbix_trapper = asus_router_logger.hooks.zabbix.ZabbixTrapper(
            sender=zabbix_sender, client_discovery_wait_time=30
        )

    await zabbix_trapper.send(_RECORD, None)

    mocked_discover_client.assert_not_called()
    zabbix_sender.send.assert_not_called()
