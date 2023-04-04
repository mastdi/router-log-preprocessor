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
import asyncio_zabbix_sender

import router_log_preprocessor.domain
import router_log_preprocessor.hooks.zabbix._known_clients as _known_clients
import router_log_preprocessor.hooks.zabbix._mapper as mapper
import router_log_preprocessor.util.rfc3164_parser

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


def _get_value(
    measurements: asyncio_zabbix_sender.Measurements, field_name: str
) -> str:
    return next(
        measurement
        for measurement in measurements._measurements
        if field_name in measurement.key.split("[")[1]
    ).value


def test_map_client_message():
    measurements = mapper.map_client_message(_RECORD, _MESSAGE)

    assert len(measurements._measurements) == 5
    assert all(
        measurement.clock == int(_RECORD.timestamp.timestamp())
        for measurement in measurements._measurements
    )
    assert all(measurement.host == _RECORD.hostname for measurement in measurements._measurements)
    assert _get_value(measurements, "location") == _MESSAGE.location
    assert int(_get_value(measurements, "status")) == _MESSAGE.status
    assert int(_get_value(measurements, "event")) == _MESSAGE.event.value
    assert int(_get_value(measurements, "rssi")) == _MESSAGE.rssi
    assert _get_value(measurements, "reason") == _MESSAGE.reason


def test_map_client_discovery():
    known_clients = _known_clients.KnownClients(42)
    known_clients.add_client(_RECORD.process, _MESSAGE.mac_address)

    measurements = mapper.map_client_discovery(_RECORD, known_clients)

    assert len(measurements._measurements) == 1
    measurement = measurements._measurements[0]
    assert measurement.clock == int(_RECORD.timestamp.timestamp())
    assert measurement.host == _RECORD.hostname
    assert measurement.value == '[{"mac":"' + str(_MESSAGE.mac_address) + '"}]'
