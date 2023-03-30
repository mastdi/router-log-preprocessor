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
import dataclasses
import enum
import json
import typing

import pyzabbix

import router_log_preprocessor.domain as domain
import router_log_preprocessor.hooks.zabbix._known_clients as _known_clients


def map_client_message(
    record: domain.LogRecord, message: domain.Message
) -> typing.List[pyzabbix.ZabbixMetric]:
    assert record.process is not None

    # Ensure process is formatted according to Zabbix recommendations
    process = record.process.lower().replace("-", "_")
    # Convert record datetime to timestamp in full seconds
    clock = int(record.timestamp.timestamp())

    # Construct the measurements from the model
    measurements = []
    model_fields = dataclasses.fields(message)
    for field in model_fields:
        if field.name == "mac_address":
            continue
        value = getattr(message, field.name)
        if isinstance(value, enum.Enum):
            value = value.value
        measurements.append(
            pyzabbix.ZabbixMetric(
                host=record.hostname,
                key=f"rlp.{process}[{field.name},{message.mac_address}]",
                value=value,
                clock=clock,
            )
        )
    return measurements


def map_client_discovery(
    record: domain.LogRecord, known_clients: _known_clients.KnownClients
) -> typing.List[pyzabbix.ZabbixMetric]:
    assert record.process is not None
    value = json.dumps(
        [{"mac": str(mac)} for mac in known_clients.clients(record.process)],
        indent=None,
        separators=(",", ":"),
    )
    return [
        pyzabbix.ZabbixMetric(
            host=record.hostname,
            key=f"rlp.client_discovery[{record.process.lower()}]",
            value=value,
            clock=int(record.timestamp.timestamp()),
        )
    ]
