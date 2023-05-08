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

import router_log_preprocessor.domain
import router_log_preprocessor.hooks.zabbix
import router_log_preprocessor.util.rfc3164_parser
from tests.hooks.util import RECORD, MESSAGE, MockedDatetime

# All test functions in this module should be tested using anyio
pytestmark = pytest.mark.anyio


async def test_discover_client_not_known(zabbix_sender):
    zabbix_trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(
        sender=zabbix_sender, client_discovery_wait_time=30
    )

    wait_time = await zabbix_trapper.discover_client(RECORD, MESSAGE)

    assert wait_time == 30
    zabbix_sender.send.assert_called_once()


async def test_discover_client_just_known(zabbix_sender):
    zabbix_trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(
        sender=zabbix_sender, client_discovery_wait_time=30
    )
    original_datetime = datetime.datetime
    first_call_time = datetime.datetime.utcnow()
    next_call_time = first_call_time + datetime.timedelta(seconds=15)
    try:
        datetime.datetime = MockedDatetime
        MockedDatetime.faked_utcnow = first_call_time
        await zabbix_trapper.discover_client(RECORD, MESSAGE)
        zabbix_sender.send.reset_mock()

        MockedDatetime.faked_utcnow = next_call_time
        wait_time = await zabbix_trapper.discover_client(RECORD, MESSAGE)
    finally:
        datetime.datetime = original_datetime
        MockedDatetime.faked_utcnow = None
    assert wait_time == 15
    zabbix_sender.send.assert_not_called()


async def test_discover_client_known_and_discovered(zabbix_sender):
    zabbix_trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(
        sender=zabbix_sender, client_discovery_wait_time=30
    )
    original_datetime = datetime.datetime
    first_call_time = datetime.datetime.utcnow()
    next_call_time = first_call_time + datetime.timedelta(seconds=42)
    try:
        datetime.datetime = MockedDatetime
        MockedDatetime.faked_utcnow = first_call_time
        await zabbix_trapper.discover_client(RECORD, MESSAGE)
        zabbix_sender.send.reset_mock()

        MockedDatetime.faked_utcnow = next_call_time
        wait_time = await zabbix_trapper.discover_client(RECORD, MESSAGE)
    finally:
        datetime.datetime = original_datetime
        MockedDatetime.faked_utcnow = None
    assert wait_time == 0
    zabbix_sender.send.assert_not_called()


async def test_send_new_client(zabbix_sender):
    total_wait_time = 42
    with unittest.mock.patch.object(
        router_log_preprocessor.hooks.zabbix.ZabbixTrapper,
        "discover_client",
        return_value=total_wait_time,
    ) as mocked_discover_client:
        trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(
            zabbix_sender, total_wait_time
        )

        with unittest.mock.patch("anyio.sleep") as mocked_sleep:
            await trapper.send(RECORD, MESSAGE)

    mocked_discover_client.assert_called()
    # Ensure that the send method adheres to the wait time
    mocked_sleep.assert_has_calls([unittest.mock.call(total_wait_time), unittest.mock.call(10)])
    zabbix_sender.send.assert_called_once()


async def test_send_known_client(zabbix_sender):
    with unittest.mock.patch.object(
        router_log_preprocessor.hooks.zabbix.ZabbixTrapper,
        "discover_client",
        return_value=0,
    ) as mocked_discover_client:
        trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(zabbix_sender, 42)

        with unittest.mock.patch("anyio.sleep") as mocked_sleep:
            await trapper.send(RECORD, MESSAGE)

    mocked_discover_client.assert_called()
    mocked_sleep.assert_called_once_with(10)
    zabbix_sender.send.assert_called_once()


async def test_send_message_none(zabbix_sender):
    with unittest.mock.patch.object(
        router_log_preprocessor.hooks.zabbix.ZabbixTrapper,
        "discover_client",
        return_value=0,
    ) as mocked_discover_client:
        zabbix_trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(
            sender=zabbix_sender, client_discovery_wait_time=30
        )

    await zabbix_trapper.send(RECORD, None)

    mocked_discover_client.assert_not_called()
    zabbix_sender.send.assert_not_called()


async def test_bundle_measurements(zabbix_sender):
    with unittest.mock.patch.object(
            router_log_preprocessor.hooks.zabbix.ZabbixTrapper,
            "discover_client",
            return_value=0,
    ) as mocked_discover_client:
        trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(zabbix_sender, 42)
        trapper._is_bundling_measurements = True

        with unittest.mock.patch("anyio.sleep") as mocked_sleep:
            await trapper.send(RECORD, MESSAGE)

    mocked_discover_client.assert_called()
    mocked_sleep.assert_not_called()
    zabbix_sender.send.assert_not_called()
