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
import logging

import asus_router_logger.settings
from asus_router_logger.domain.mac_base import MAC
from asus_router_logger.domain.wlc import WlcEvent, WlcEventModel
from asus_router_logger.log_server.rfc3164_parser import LogRecord


def handle_wireless_lan_controller_event(record: LogRecord) -> WlcEventModel:
    settings = asus_router_logger.settings.settings()
    logger = logging.getLogger(settings.logging_name_base)
    logger.debug("Received WLC event daemon log: %r", record)

    # Remove message type from the message, i.e. wlceventd_proc_event(xxx):
    message = record.message[record.message.find(": ") + 2 :]
    # The parts come in a comma separated list of key:value pairs
    message_parts = message.split(", ")
    # First part contains location and event
    location, event = message_parts[0].split(":", maxsplit=1)
    # A mac address is 17 characters long and is found as the last part of the event
    mac_address = event[-17:]
    # Next part is status
    assert message_parts[1].startswith("status")
    status = message_parts[1].split(":")[1]
    # Next part is reason of the event
    assert message_parts[2].startswith("reason")
    reason = message_parts[2].split(":")[1]
    # Last part is the Received Signal Strength Indicator
    assert message_parts[3].startswith("rssi")
    rssi = message_parts[3].split(":")[1]

    return WlcEventModel(
        mac_address=MAC(mac_address),
        event=WlcEvent.from_reason(reason),
        location=location,
        status=int(status),
        rssi=int(rssi),
    )
