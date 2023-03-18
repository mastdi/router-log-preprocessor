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
import typing

import pyzabbix

import asus_router_logger.domain
import asus_router_logger.hooks.zabbix._mapper as mapper
import asus_router_logger.util.rfc3164_parser

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


def _get_value(
    measurements: typing.List[pyzabbix.ZabbixMetric], field_name: str
) -> str:
    return next(
        measurement
        for measurement in measurements
        if field_name in measurement.key.split("[")[1]
    ).value


def test_map_client_message():
    measurements = mapper.map_client_message(_RECORD, _MESSAGE)

    assert len(measurements) == 5
    assert all(
        measurement.clock == int(_RECORD.timestamp.timestamp())
        for measurement in measurements
    )
    assert all(measurement.host == _RECORD.hostname for measurement in measurements)
    assert _get_value(measurements, "location") == _MESSAGE.location
    assert int(_get_value(measurements, "status")) == _MESSAGE.status
    assert int(_get_value(measurements, "event")) == _MESSAGE.event.value
    assert int(_get_value(measurements, "rssi")) == _MESSAGE.rssi
    assert _get_value(measurements, "reason") == _MESSAGE.reason
