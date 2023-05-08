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

import asyncio_zabbix_sender

import router_log_preprocessor.domain
import router_log_preprocessor.hooks.zabbix._known_clients as _known_clients
import router_log_preprocessor.hooks.zabbix._mapper as mapper
import router_log_preprocessor.util.rfc3164_parser
from tests.hooks.util import MESSAGE, RECORD


def _get_value(
    measurements: asyncio_zabbix_sender.Measurements, field_name: str
) -> str:
    return next(
        measurement
        for measurement in measurements
        if field_name in measurement.key.split("[")[1]
    ).value


def test_map_client_message():
    measurements = [
        measurement
        for measurement in mapper.map_client_message(RECORD, MESSAGE)
    ]

    assert len(measurements) == 5
    assert all(
        measurement.clock == int(RECORD.timestamp.timestamp())
        for measurement in measurements
    )
    assert all(measurement.host == RECORD.hostname for measurement in measurements)
    assert _get_value(measurements, "location") == MESSAGE.location
    assert int(_get_value(measurements, "status")) == MESSAGE.status
    assert int(_get_value(measurements, "event")) == MESSAGE.event.value
    assert int(_get_value(measurements, "rssi")) == MESSAGE.rssi
    assert _get_value(measurements, "reason") == MESSAGE.reason


def test_map_client_message_dhcp():
    message = router_log_preprocessor.domain.DnsmasqDhcpAcknowledge(
        mac_address=router_log_preprocessor.domain.MAC("AB:CD:EF:01:23:45"),
        ip_address=ipaddress.IPv4Address("192.168.101.149"),
        hostname="fake-client"
    )

    measurements = [
        measurement
        for measurement in mapper.map_client_message(RECORD, message)
    ]

    assert len(measurements) == 2
    assert all(
        measurement.clock == int(RECORD.timestamp.timestamp())
        for measurement in measurements
    )
    assert _get_value(measurements, "ip_address") == str(message.ip_address)
    assert _get_value(measurements, "hostname") == message.hostname


def test_map_client_discovery():
    known_clients = _known_clients.KnownClients(42)
    known_clients.add_client(RECORD.process, MESSAGE.mac_address)

    measurements = mapper.map_client_discovery(RECORD, known_clients)

    assert len(measurements._measurements) == 1
    measurement = measurements._measurements[0]
    assert measurement.clock == int(RECORD.timestamp.timestamp())
    assert measurement.host == RECORD.hostname
    assert measurement.value == '[{"mac":"' + str(MESSAGE.mac_address) + '"}]'
