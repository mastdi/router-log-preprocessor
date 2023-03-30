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

import router_log_preprocessor.domain as domain
import router_log_preprocessor.util.logging as logging

_KNOWN_MESSAGE_PARTS = frozenset(("reason", "status", "rssi"))


def preprocess_wireless_lan_controller_event(
    record: domain.LogRecord,
) -> domain.WlcEventModel:
    logging.logger.debug("Received WLC event daemon log: %r", record)

    # Remove message type from the message, i.e. wlceventd_proc_event(xxx):
    message = record.message[record.message.find(": ") + 2 :]
    # The parts come in a comma separated list of key:value pairs
    message_parts: typing.Dict[str, str] = dict()
    for pair in message.split(", "):
        key, value = pair.split(":", maxsplit=1)
        message_parts[key] = value

    # Find the location:event pair, i.e. the only unknown key
    unknown_parts = list(set(message_parts.keys()).difference(_KNOWN_MESSAGE_PARTS))
    assert len(unknown_parts) == 1, unknown_parts
    location = unknown_parts.pop()
    # Process the event part
    event = message_parts[location]
    # A mac address is 17 characters long and is found as the last part of the event
    mac_address = event[-17:]

    # Process the status
    try:
        status = int(message_parts["status"])
    except ValueError:
        # Status is a text string with the status code in parentheses,
        # e.g. "Successful (0)"
        status = int(
            message_parts["status"][message_parts["status"].find("(") + 1 : -1]
        )

    return domain.WlcEventModel(
        mac_address=domain.MAC(mac_address),
        event=domain.WlcEvent.from_event(event),
        reason=message_parts.get("reason", ""),
        location=location,
        status=status,
        rssi=int(message_parts["rssi"]),
    )
