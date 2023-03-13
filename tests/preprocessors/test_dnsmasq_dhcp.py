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
import ipaddress

import pytest

import asus_router_logger.domain as domain
import asus_router_logger.util.rfc3164_parser
from asus_router_logger.preprocessors.dnsmasq_dhcp import preprocess_dnsmasq_dhcp_event


def _log_record_factory(message: str) -> asus_router_logger.domain.LogRecord:
    return asus_router_logger.domain.LogRecord(
        facility=1,
        severity=5,
        timestamp=asus_router_logger.util.rfc3164_parser.timestamp_to_datetime(
            "Feb", "2", "13", "02", "51"
        ),
        hostname="GT-AX11000-ABCD-1234567-E",
        process="dnsmasq-dhcp",
        process_id=2971,
        message=message,
    )


def test_dhcp_ack():
    record = _log_record_factory(
        "DHCPACK(br1) 192.168.101.149 ab:cd:ef:01:23:45 fake-client"
    )

    model = preprocess_dnsmasq_dhcp_event(record)

    assert model is not None
    assert model.mac_address == domain.MAC("AB:CD:EF:01:23:45")
    assert model.ip_address == ipaddress.IPv4Address("192.168.101.149")
    assert model.hostname == "fake-client"


def test_dhcp_ack_without_hostname():
    record = _log_record_factory("DHCPACK(br1) 192.168.101.216 01:23:45:67:89:AB")

    model = preprocess_dnsmasq_dhcp_event(record)

    assert model is not None
    assert model.mac_address == domain.MAC("01:23:45:67:89:AB")
    assert model.ip_address == ipaddress.IPv4Address("192.168.101.216")
    assert model.hostname == ""


@pytest.mark.parametrize(
    argnames="message",
    argvalues=(
        "DHCPDISCOVER(br1) ab:cd:ef:01:23:45",
        "DHCPOFFER(br1) 192.168.101.149 ab:cd:ef:01:23:45",
        "DHCPREQUEST(br1) 192.168.101.149 ab:cd:ef:01:23:45",
    ),
)
def test_dhcp_other_events(message: str):
    record = _log_record_factory(message)

    model = preprocess_dnsmasq_dhcp_event(record)

    assert model is None
