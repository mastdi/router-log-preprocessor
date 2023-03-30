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
import unittest.mock

import pytest

import router_log_preprocessor.preprocessors.dnsmasq_dhcp as dnsmasq_dhcp
import router_log_preprocessor.preprocessors.wlc as wlc
from router_log_preprocessor.log_server.handler import LogHandler


@pytest.fixture
def anyio_backend():
    return "asyncio"


pytestmark = pytest.mark.anyio


@pytest.fixture
def mock_zabbix_trapper():
    zabbix_trapper = unittest.mock.MagicMock()
    zabbix_trapper.send = unittest.mock.AsyncMock()
    return zabbix_trapper


@pytest.fixture
def log_handler(mock_zabbix_trapper):

    return LogHandler(
        {
            "wlceventd": wlc.preprocess_wireless_lan_controller_event,
            "dnsmasq-dhcp": dnsmasq_dhcp.preprocess_dnsmasq_dhcp_event,
        },
        [mock_zabbix_trapper],
    )


async def test_log_handler_handle_wlc(mock_zabbix_trapper, log_handler):
    packet = (
        b"<6>Oct 18 14:02:56 GT-AX11000-ABCD-1234567-E wlceventd: "
        b"wlceventd_proc_event(431): eth1: Auth ab:cd:ef:01:23:45, "
        b"status: successful (0), rssi:-70"
    )
    host = "127.0.0.1"
    port = 514

    await log_handler.handle(packet, host, port)

    mock_zabbix_trapper.send.assert_called_once()


async def test_log_handler_handle_dnsmasq(mock_zabbix_trapper, log_handler):
    packet = (
        b"<6>Feb  2 13:02:51 GT-AX11000-ABCD-1234567-E dnsmasq-dhcp[2971]: "
        b"DHCPACK(br1) 192.168.101.149 ab:cd:ef:01:23:45 fake-client"
    )
    host = "127.0.0.1"
    port = 514

    await log_handler.handle(packet, host, port)

    mock_zabbix_trapper.send.assert_called_once()


async def test_log_handler_handle_unknown(mock_zabbix_trapper, log_handler):
    packet = (
        b"<6>Oct 18 14:02:56 GT-AX11000-ABCD-1234567-E unknown_process: Some message"
    )
    host = "127.0.0.1"
    port = 514

    await log_handler.handle(packet, host, port)

    args = mock_zabbix_trapper.send.call_args[0]
    kwargs = mock_zabbix_trapper.send.call_args[1]
    if "message" in kwargs:
        assert kwargs["message"] is None
    elif len(args) == 2:
        # send was called with args and not kwargs and message is the last positional
        # argument
        assert args[1] is None
    else:
        assert False, (
            "This test must check that the ZabbixTrapper.send have been "
            "called at with a None message."
        )
